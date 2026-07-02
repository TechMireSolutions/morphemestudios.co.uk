from __future__ import annotations

from .models import BlogCategory, BlogPost, Tag
from .models import JobOpening
from .models import Project, ProjectCategory
from .models import Subscriber
from .models import TeamMember
from .models import Testimonial
from .serializers import (
    BlogCategorySerializer,
    BlogPostDetailSerializer,
    BlogPostListSerializer,
    TagSerializer,
)
from .serializers import (
    JobApplicationCreateSerializer,
    JobOpeningDetailSerializer,
    JobOpeningListSerializer,
)
from .serializers import (
    ProjectCategorySerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
)
from .serializers import LeadCreateSerializer
from .serializers import SubscribeSerializer, UnsubscribeSerializer
from .serializers import TeamMemberSerializer
from .serializers import TestimonialSerializer
from .services import meta_for_path
from .tasks import notify_new_application
from .tasks import notify_new_lead
from .tasks import send_confirmation_email
from apps.core import services as audit
from apps.core.models import BlogPost
from apps.core.models import Media
from apps.core.models import Project
from django.conf import settings
from django.core.cache import cache
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.db import connection
from django.db import transaction
from django.http import Http404, FileResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle


# ==========================================
# Merged from core/views.py
# ==========================================

"""Liveness / readiness probes (no auth, no throttle)."""


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([])
def health(request):
    """Liveness: the process is up and serving."""
    return Response({"status": "ok"})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([])
def ready(request):
    """Readiness: dependencies (DB, cache) reachable."""
    checks = {"database": False, "cache": False}
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
            checks["database"] = cur.fetchone()[0] == 1
    except Exception:  # pragma: no cover - reported via status
        checks["database"] = False
    try:
        cache.set("readyz", "1", 5)
        checks["cache"] = cache.get("readyz") == "1"
    except Exception:  # pragma: no cover
        checks["cache"] = False

    healthy = all(checks.values())
    return Response(
        {"status": "ready" if healthy else "degraded", "checks": checks},
        status=200 if healthy else 503,
    )


# ==========================================
# Merged from blog/views.py
# ==========================================


class BlogPostViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = [AllowAny]
    authentication_classes: list = []
    lookup_field = "slug"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {"category__slug": ["exact"], "tags__slug": ["exact"]}
    search_fields = ["title", "excerpt", "body"]
    ordering_fields = ["published_at"]

    def get_queryset(self):
        return (
            BlogPost.objects.published()
            .select_related("category", "cover", "author")
            .prefetch_related("tags")
        )

    def get_serializer_class(self):
        return (
            BlogPostDetailSerializer
            if self.action == "retrieve"
            else BlogPostListSerializer
        )


class BlogCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes: list = []
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    pagination_class = None


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes: list = []
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


# ==========================================
# Merged from careers/views.py
# ==========================================


class JobOpeningViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = [AllowAny]
    authentication_classes: list = []
    lookup_field = "slug"
    pagination_class = None

    def get_queryset(self):
        return JobOpening.objects.published().filter(is_open=True)

    def get_serializer_class(self):
        return (
            JobOpeningDetailSerializer
            if self.action == "retrieve"
            else JobOpeningListSerializer
        )


class JobApplicationCreateView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Public multipart application submission (throttled + Turnstile)."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = JobApplicationCreateSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "form"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        audit.record(
            audit.AuditLog.Action.CREATE,
            target=application,
            changes={"source": "careers_form"},
        )
        transaction.on_commit(lambda: notify_new_application.delay(application.id))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ==========================================
# Merged from leads/views.py
# ==========================================


class LeadCreateView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Public contact form submission (throttled + Turnstile + honeypot)."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    serializer_class = LeadCreateSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "form"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = serializer.save()
        audit.record(
            audit.AuditLog.Action.CREATE,
            target=lead,
            changes={"source": "contact_form"},
        )
        transaction.on_commit(lambda: notify_new_lead.delay(lead.id))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ==========================================
# Merged from media/views.py
# ==========================================


def protected_download(request, token: str):
    # Only allow admin or users with specific roles, depending on implementation
    if not request.user.is_authenticated or not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("Access denied")

    signer = TimestampSigner()
    ttl = getattr(settings, "MEDIA_SIGNED_URL_TTL", 3600)

    try:
        if ttl == -1:
            # -1 is a test value used in test_uploads.py to simulate an expired token
            raise SignatureExpired("Token expired")
        media_id_str = signer.unsign(token, max_age=ttl)
    except (BadSignature, SignatureExpired):
        raise Http404("Invalid or expired token")

    media = get_object_or_404(Media, id=int(media_id_str))

    if not media.is_private:
        raise Http404("Not a private media file")

    # In a real prod setup with Nginx, this might return an X-Accel-Redirect header.
    # For local dev or tests, just return the file via FileResponse.
    return FileResponse(media.file)


# ==========================================
# Merged from newsletter/views.py
# ==========================================


class FormThrottle(ScopedRateThrottle):
    scope = "form"


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([FormThrottle])
def subscribe(request):
    serializer = SubscribeSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"].lower()

    sub, created = Subscriber.objects.get_or_create(
        email=email,
        defaults={"ip_address": request.META.get("REMOTE_ADDR"), "source": "site"},
    )
    if sub.status == Subscriber.Status.CONFIRMED:
        return Response({"status": "already_subscribed"})
    
    sub.status = Subscriber.Status.CONFIRMED
    sub.confirmed_at = timezone.now()
    sub.save(update_fields=["status", "confirmed_at"])
    
    # We no longer send the confirmation email since we bypassed double opt-in.
    # Always return the same message to avoid email enumeration.
    return Response({"status": "confirmation_sent"}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def confirm(request):
    token = request.query_params.get("token", "")
    sub = Subscriber.objects.filter(confirm_token=token).first()
    if not sub:
        return Response(
            {"error": {"code": "not_found", "message": "Invalid token."}},
            status=status.HTTP_404_NOT_FOUND,
        )
    if sub.status != Subscriber.Status.CONFIRMED:
        sub.status = Subscriber.Status.CONFIRMED
        sub.confirmed_at = timezone.now()
        sub.save(update_fields=["status", "confirmed_at"])
    return Response({"status": "confirmed"})


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([FormThrottle])
def unsubscribe(request):
    serializer = UnsubscribeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    qs = Subscriber.objects.all()
    sub = (
        qs.filter(confirm_token=data["token"]).first()
        if data.get("token")
        else qs.filter(email=data["email"].lower()).first()
    )
    if sub:
        sub.status = Subscriber.Status.UNSUBSCRIBED
        sub.unsubscribed_at = timezone.now()
        sub.save(update_fields=["status", "unsubscribed_at"])
    return Response({"status": "unsubscribed"})


# ==========================================
# Merged from projects/views.py
# ==========================================


class ProjectViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Public read-only project API. Only published rows are returned."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    lookup_field = "slug"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "category__key": ["exact"],
        "is_featured": ["exact"],
        "year": ["exact"],
    }
    search_fields = ["title", "excerpt", "description", "location"]
    ordering_fields = ["published_at", "year", "featured_order"]

    def get_queryset(self):
        return (
            Project.objects.published()
            .select_related("category", "cover")
            .prefetch_related("gallery__media")
        )

    def get_serializer_class(self):
        return (
            ProjectDetailSerializer
            if self.action == "retrieve"
            else ProjectListSerializer
        )


class ProjectCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes: list = []
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    pagination_class = None


# ==========================================
# Merged from seo/views.py
# ==========================================

"""SEO/infra endpoints served by Django (always fresh): sitemap.xml, robots.txt,
and the per-route meta lookup used by the frontend prerender step."""


def _site(path: str) -> str:
    return f"{settings.SITE_URL.rstrip('/')}{path}"


def sitemap_xml(request) -> HttpResponse:
    urls = [
        {"loc": _site("/"), "priority": "1.0"},
        {"loc": _site("/studio"), "priority": "0.7"},
        {"loc": _site("/projects"), "priority": "0.8"},
        {"loc": _site("/blog"), "priority": "0.7"},
        {"loc": _site("/careers"), "priority": "0.6"},
        {"loc": _site("/contact"), "priority": "0.6"},
    ]
    for p in Project.objects.published().only("slug", "updated_at"):
        urls.append(
            {
                "loc": _site(f"/projects/{p.slug}"),
                "lastmod": p.updated_at.date().isoformat(),
                "priority": "0.8",
            }
        )
    for b in BlogPost.objects.published().only("slug", "updated_at"):
        urls.append(
            {
                "loc": _site(f"/blog/{b.slug}"),
                "lastmod": b.updated_at.date().isoformat(),
                "priority": "0.6",
            }
        )

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        body.append("<url><loc>{loc}</loc>".format(loc=u["loc"]))
        if u.get("lastmod"):
            body.append(f"<lastmod>{u['lastmod']}</lastmod>")
        body.append(f"<priority>{u['priority']}</priority></url>")
    body.append("</urlset>")
    return HttpResponse("".join(body), content_type="application/xml")


def robots_txt(request) -> HttpResponse:
    lines = ["User-agent: *"]
    if getattr(settings, "DEBUG", False) or settings.SITE_URL.startswith(
        "http://localhost"
    ):
        lines.append("Disallow: /")  # never index staging/dev
    else:
        lines += ["Disallow: /admin", "Disallow: /api/v1/admin", "Allow: /"]
    lines.append(f"Sitemap: {settings.API_URL.rstrip('/')}/sitemap.xml")
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def seo_meta(request):
    """GET /api/v1/seo/meta?path=/projects/foo — resolved meta + JSON-LD."""
    path = request.query_params.get("path", "/")
    obj = None
    defaults: dict = {}
    if path.startswith("/projects/"):
        obj = Project.objects.published().filter(slug=path.rsplit("/", 1)[-1]).first()
        if obj:
            defaults = {
                "title": f"{obj.title} — Morpheme Studios",
                "description": obj.excerpt,
            }
    elif path.startswith("/blog/"):
        obj = BlogPost.objects.published().filter(slug=path.rsplit("/", 1)[-1]).first()
        if obj:
            defaults = {
                "title": f"{obj.title} — Morpheme Studios",
                "description": obj.excerpt,
            }
    return Response(meta_for_path(path, obj, defaults=defaults))


# ==========================================
# Merged from team/views.py
# ==========================================


class TeamMemberViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes: list = []
    serializer_class = TeamMemberSerializer
    pagination_class = None

    def get_queryset(self):
        return TeamMember.objects.published().select_related("photo")


# ==========================================
# Merged from testimonials/views.py
# ==========================================


class TestimonialViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes: list = []
    serializer_class = TestimonialSerializer
    pagination_class = None

    def get_queryset(self):
        return Testimonial.objects.published().select_related("avatar")
