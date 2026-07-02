from __future__ import annotations

from .models import AuditLog
from .models import BlogPost
from .models import JobApplication
from .models import Lead, LeadNote
from .models import Project
from .models import TeamMember
from .models import Testimonial
from apps.core import services as audit
from apps.core.permissions import CanManageApplications
from apps.core.permissions import CanManageContent
from apps.core.permissions import CanManageLeads
from apps.core.permissions import IsAdminLevel
from apps.core.permissions import IsStaff
from apps.core.signing import make_token
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


# ==========================================
# Merged from core/admin_api.py
# ==========================================

"""Admin dashboard KPIs (architecture §4). Cached briefly in Redis."""


@api_view(["GET"])
@permission_classes([IsStaff])
def dashboard_stats(request):
    cached = cache.get("dashboard_stats")
    if cached:
        return Response(cached)

    from apps.core.models import BlogPost
    from apps.core.models import JobApplication
    from apps.core.models import PublishStatus
    from apps.core.models import Lead
    from apps.core.models import Subscriber
    from apps.core.models import Project

    now = timezone.now()
    last7 = now - timedelta(days=7)
    last30 = now - timedelta(days=30)

    data = {
        "leads": {
            "new_7d": Lead.objects.filter(created_at__gte=last7).count(),
            "new_30d": Lead.objects.filter(created_at__gte=last30).count(),
            "open": Lead.objects.exclude(status__in=["won", "lost"]).count(),
        },
        "applications": {
            "new_7d": JobApplication.objects.filter(created_at__gte=last7).count(),
            "new_30d": JobApplication.objects.filter(created_at__gte=last30).count(),
        },
        "content": {
            "projects_published": Project.objects.filter(
                status=PublishStatus.PUBLISHED
            ).count(),
            "projects_draft": Project.objects.filter(
                status=PublishStatus.DRAFT
            ).count(),
            "posts_published": BlogPost.objects.filter(
                status=PublishStatus.PUBLISHED
            ).count(),
            "posts_draft": BlogPost.objects.filter(status=PublishStatus.DRAFT).count(),
        },
        "newsletter": {
            "confirmed": Subscriber.objects.filter(status="confirmed").count(),
            "pending": Subscriber.objects.filter(status="pending").count(),
        },
    }
    cache.set("dashboard_stats", data, 60)
    return Response(data)


# ==========================================
# Merged from audit/admin_api.py
# ==========================================


class AuditLogSerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source="actor.email", default=None, read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "actor",
            "action",
            "target_type",
            "target_id",
            "changes",
            "ip_address",
            "created_at",
        )


class AuditLogViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAdminLevel]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.select_related("actor")
    filterset_fields = ["action", "target_type", "actor"]
    search_fields = ["target_type", "target_id", "actor__email"]
    ordering_fields = ["created_at"]


# ==========================================
# Merged from blog/admin_api.py
# ==========================================

"""Admin CRUD API for Blog posts (RBAC: CanManageContent).

Body HTML is sanitized in BlogPost.save() (nh3), so write access here is XSS-safe.
"""


class AdminBlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = (
            "id",
            "slug",
            "title",
            "excerpt",
            "body",
            "cover",
            "category",
            "tags",
            "author",
            "reading_minutes",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AdminBlogPostViewSet(viewsets.ModelViewSet):
    permission_classes = [CanManageContent]
    serializer_class = AdminBlogPostSerializer
    filterset_fields = ["status", "category__slug", "tags__slug"]
    search_fields = ["title", "excerpt", "body"]
    ordering_fields = ["published_at", "created_at"]

    def get_queryset(self):
        return BlogPost.objects.select_related(
            "category", "cover", "author"
        ).prefetch_related("tags")

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        audit.record(audit.AuditLog.Action.CREATE, target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        audit.record(audit.AuditLog.Action.UPDATE, target=obj)

    def perform_destroy(self, instance):
        audit.record(audit.AuditLog.Action.DELETE, target=instance)
        instance.delete()


# ==========================================
# Merged from careers/admin_api.py
# ==========================================

"""Admin REST API for reviewing applications (RBAC-gated). File access only via
short-lived signed URLs — raw private paths are never exposed."""


class AdminApplicationSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = (
            "id",
            "opening",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "nationality",
            "country_of_residence",
            "home_address",
            "email",
            "phone",
            "field_of_expertise",
            "applying_for",
            "education",
            "experience_range",
            "status",
            "assigned_to",
            "files",
            "created_at",
        )
        read_only_fields = tuple(
            f for f in fields if f not in {"status", "assigned_to"}
        )

    def get_files(self, obj: JobApplication) -> dict:
        out = {}
        for kind in ("cv", "portfolio", "cover_letter"):
            media = getattr(obj, kind)
            out[kind] = bool(media)
        return out


class AdminApplicationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [CanManageApplications]
    serializer_class = AdminApplicationSerializer
    filterset_fields = ["status", "opening"]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        return JobApplication.objects.select_related(
            "opening", "assigned_to", "cv", "portfolio", "cover_letter"
        )

    def perform_update(self, serializer):
        app = serializer.save()
        audit.record(audit.AuditLog.Action.UPDATE, target=app)

    @action(
        detail=True,
        methods=["get"],
        url_path=r"files/(?P<kind>cv|portfolio|cover_letter)/signed-url",
    )
    def signed_url(self, request, pk=None, kind=None):
        app = self.get_object()
        media = getattr(app, kind, None)
        if not media:
            return Response(
                {"error": {"code": "not_found", "message": "No such file."}}, status=404
            )
        from django.conf import settings

        token = make_token(media.id)
        audit.record(
            audit.AuditLog.Action.UPDATE, target=app, changes={"downloaded": kind}
        )
        return Response(
            {"url": f"/protected/{token}", "expires_in": settings.MEDIA_SIGNED_URL_TTL}
        )


# ==========================================
# Merged from leads/admin_api.py
# ==========================================

"""Admin REST API for the leads pipeline (RBAC-gated). Complements the Django
Admin CMS for a future custom React dashboard (architecture §4/§7.5)."""


class LeadNoteSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = LeadNote
        fields = ("id", "body", "author", "created_at")
        read_only_fields = ("id", "author", "created_at")


class LeadSerializer(serializers.ModelSerializer):
    notes = LeadNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "message",
            "status",
            "source",
            "assigned_to",
            "spam_score",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "name",
            "email",
            "phone",
            "message",
            "source",
            "spam_score",
            "notes",
            "created_at",
            "updated_at",
        )


class AdminLeadViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [CanManageLeads]
    serializer_class = LeadSerializer
    filterset_fields = ["status", "assigned_to"]
    search_fields = ["name", "email", "message"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        return Lead.objects.prefetch_related("notes__author").select_related(
            "assigned_to"
        )

    def perform_update(self, serializer):
        lead = serializer.save()
        audit.record(
            audit.AuditLog.Action.UPDATE,
            target=lead,
            changes={
                k: serializer.validated_data[k] for k in serializer.validated_data
            },
        )

    @action(detail=True, methods=["post"])
    def notes(self, request, pk=None):
        lead = self.get_object()
        body = (request.data or {}).get("body", "").strip()
        if not body:
            return Response(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Note body required.",
                    }
                },
                status=400,
            )
        note = LeadNote.objects.create(lead=lead, author=request.user, body=body)
        audit.record(audit.AuditLog.Action.CREATE, target=note)
        return Response(LeadNoteSerializer(note).data, status=201)


# ==========================================
# Merged from projects/admin_api.py
# ==========================================

"""Admin CRUD API for Projects (RBAC: CanManageContent). Complements the public
read API and Django Admin for a future custom React dashboard (architecture §7.5)."""


class AdminProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "slug",
            "title",
            "location",
            "year",
            "category",
            "type",
            "status_label",
            "excerpt",
            "description",
            "services",
            "cover",
            "is_featured",
            "featured_order",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AdminProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [CanManageContent]
    serializer_class = AdminProjectSerializer
    filterset_fields = ["status", "category__key", "is_featured"]
    search_fields = ["title", "excerpt", "description", "location"]
    ordering_fields = ["published_at", "featured_order", "year", "created_at"]

    def get_queryset(self):
        return Project.objects.select_related("category", "cover").all()

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        audit.record(audit.AuditLog.Action.CREATE, target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        audit.record(audit.AuditLog.Action.UPDATE, target=obj)

    def perform_destroy(self, instance):
        audit.record(audit.AuditLog.Action.DELETE, target=instance)
        instance.delete()


# ==========================================
# Merged from team/admin_api.py
# ==========================================

"""Admin CRUD API for Team members (RBAC: CanManageContent)."""


class AdminTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = (
            "id",
            "name",
            "role",
            "bio",
            "photo",
            "sort_order",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AdminTeamMemberViewSet(viewsets.ModelViewSet):
    permission_classes = [CanManageContent]
    serializer_class = AdminTeamMemberSerializer
    filterset_fields = ["status"]
    search_fields = ["name", "role"]
    ordering_fields = ["sort_order", "created_at"]

    def get_queryset(self):
        return TeamMember.objects.select_related("photo").all()

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        audit.record(audit.AuditLog.Action.CREATE, target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        audit.record(audit.AuditLog.Action.UPDATE, target=obj)

    def perform_destroy(self, instance):
        audit.record(audit.AuditLog.Action.DELETE, target=instance)
        instance.delete()


# ==========================================
# Merged from testimonials/admin_api.py
# ==========================================

"""Admin CRUD API for Testimonials (RBAC: CanManageContent)."""


class AdminTestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = (
            "id",
            "author_name",
            "author_role",
            "company",
            "quote",
            "rating",
            "avatar",
            "sort_order",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AdminTestimonialViewSet(viewsets.ModelViewSet):
    permission_classes = [CanManageContent]
    serializer_class = AdminTestimonialSerializer
    filterset_fields = ["status", "rating"]
    search_fields = ["author_name", "company", "quote"]
    ordering_fields = ["sort_order", "created_at"]

    def get_queryset(self):
        return Testimonial.objects.select_related("avatar").all()

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        audit.record(audit.AuditLog.Action.CREATE, target=obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        audit.record(audit.AuditLog.Action.UPDATE, target=obj)

    def perform_destroy(self, instance):
        audit.record(audit.AuditLog.Action.DELETE, target=instance)
        instance.delete()
