from __future__ import annotations

from apps.core.sanitize import sanitize_html
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import os
import secrets
import uuid


# ==========================================
# Merged from core/models.py
# ==========================================

"""Shared abstract bases + site-wide config models.

The abstract bases (`TimeStampedModel`, `PublishableModel`) carry the common
columns described in the architecture doc §2.2 so every content table stays
consistent. The concrete models here are the low-churn site config collections
(offices, settings, redirects, editable static pages).
"""


class TimeStampedModel(models.Model):
    """`created_at` / `updated_at` / `created_by` on every content table."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        abstract = True


class PublishStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class PublishedQuerySet(models.QuerySet):
    def published(self) -> "PublishedQuerySet":
        return self.filter(status=PublishStatus.PUBLISHED)


class PublishableModel(TimeStampedModel):
    """Adds the draft/published/archived workflow. Only `published` rows are
    ever returned by the public API."""

    status = models.CharField(
        max_length=12,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField(null=True, blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Site config collections
# ---------------------------------------------------------------------------
class Office(models.Model):
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    address_lines = models.JSONField(default=list, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "city"]

    def __str__(self) -> str:
        return f"{self.city}, {self.country}"


class SiteSetting(models.Model):
    """Key/value site config (mission, approach, stats, social URLs)."""

    key = models.SlugField(max_length=80, unique=True)
    value = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.key


class RedirectRule(models.Model):
    """301/302 management so old WordPress URLs don't 404 (SEO §9)."""

    STATUS_CHOICES = [(301, "301 Permanent"), (302, "302 Temporary")]

    from_path = models.CharField(max_length=512, unique=True, db_index=True)
    to_path = models.CharField(max_length=512)
    status_code = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=301)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.from_path} -> {self.to_path} ({self.status_code})"


class Page(PublishableModel):
    """Editable static pages (home, studio, terms) as block JSON."""

    key = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=200)
    blocks = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.key


# ==========================================
# Merged from audit/models.py
# ==========================================

"""Append-only audit trail for staff mutations (security §6)."""


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        LOGIN = "login", "Login"
        LOGIN_FAILED = "login_failed", "Login failed"
        LOGOUT = "logout", "Logout"
        PERMISSION_DENIED = "permission_denied", "Permission denied"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_entries",
    )
    action = models.CharField(max_length=32, choices=Action.choices)
    target_type = models.CharField(max_length=120, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["target_type", "target_id"]),
            models.Index(fields=["actor", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.target_type}#{self.target_id} by {self.actor_id}"


# ==========================================
# Merged from blog/models.py
# ==========================================

"""Blog (thought-leadership). Adds the real article body the old site had
but the new SPA dropped (audit §3)."""


class BlogCategory(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    label = models.CharField(max_length=120)

    class Meta:
        verbose_name_plural = "Blog categories"
        ordering = ["label"]

    def __str__(self) -> str:
        return self.label


class Tag(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    label = models.CharField(max_length=120)

    class Meta:
        ordering = ["label"]

    def __str__(self) -> str:
        return self.label


class BlogPost(PublishableModel):
    slug = models.SlugField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    excerpt = models.CharField(max_length=400, blank=True)
    body = models.TextField(blank=True, help_text="Sanitised HTML / rich text")
    cover = models.ForeignKey(
        "core.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    category = models.ForeignKey(
        BlogCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="posts",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_posts",
    )
    reading_minutes = models.PositiveSmallIntegerField(default=3)

    seo = GenericRelation("core.SeoMeta")

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["category", "status"]),
        ]

    def save(self, *args, **kwargs):
        # Sanitize rich-text HTML at write time (stored-XSS defense). Applies to
        # every write path: Django Admin, data import, and any future API.
        self.body = sanitize_html(self.body)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


# ==========================================
# Merged from careers/models.py
# ==========================================

"""Careers: openings (CMS-managed) + applications (system-generated, PII +
private file uploads). Applications are read-only in admin; files reachable
only via short-lived signed URLs (security §6)."""


class JobOpening(PublishableModel):
    slug = models.SlugField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    place = models.CharField(max_length=200, blank=True)
    employment_type = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    requirements = models.JSONField(default=list, blank=True)
    is_open = models.BooleanField(default=True)
    closes_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class JobApplication(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        SCREENING = "screening", "Screening"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        HIRED = "hired", "Hired"
        REJECTED = "rejected", "Rejected"

    opening = models.ForeignKey(
        JobOpening,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="applications",
        help_text="Null = speculative application",
    )

    # Applicant PII
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    gender = models.CharField(max_length=40, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=120, blank=True)
    country_of_residence = models.CharField(max_length=120, blank=True)
    home_address = models.TextField(blank=True)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=40, blank=True)
    field_of_expertise = models.CharField(max_length=200, blank=True)
    applying_for = models.CharField(max_length=200, blank=True)
    education = models.TextField(blank=True)
    experience_range = models.CharField(max_length=80, blank=True)

    # Private uploads (PDF only). is_private=True on each Media.
    cv = models.ForeignKey(
        "core.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    portfolio = models.ForeignKey(
        "core.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    cover_letter = models.ForeignKey(
        "core.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.RECEIVED, db_index=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_applications",
    )
    source = models.CharField(max_length=80, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["opening"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(terms_accepted=True), name="application_terms_required"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} <{self.email}>"


# ==========================================
# Merged from leads/models.py
# ==========================================

"""Leads = contact-form enquiries + pipeline (architecture §2.2 / §4)."""


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        PROPOSAL = "proposal", "Proposal"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    name = models.CharField(max_length=200)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField()

    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.NEW, db_index=True
    )
    source = models.CharField(max_length=80, blank=True, default="contact_form")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_leads",
    )
    spam_score = models.FloatField(default=0.0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["assigned_to"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


class LeadNote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Note on lead #{self.lead_id}"


# ==========================================
# Merged from media/models.py
# ==========================================


def media_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join(
        "uploads" if not instance.is_private else "private_uploads", filename
    )


class Media(models.Model):
    class Type(models.TextChoices):
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"
        DOCUMENT = "DOCUMENT", "Document"

    type = models.CharField(max_length=20, choices=Type.choices, default=Type.IMAGE)
    is_private = models.BooleanField(default=False)
    original_name = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)
    mime = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to=media_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Media"

    def __str__(self):
        return self.original_name


# ==========================================
# Merged from newsletter/models.py
# ==========================================

"""Newsletter subscribers with double opt-in (architecture §7.2)."""


def _token() -> str:
    return secrets.token_urlsafe(32)


class Subscriber(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending confirmation"
        CONFIRMED = "confirmed", "Confirmed"
        UNSUBSCRIBED = "unsubscribed", "Unsubscribed"

    email = models.EmailField(unique=True)
    status = models.CharField(
        max_length=14, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    confirm_token = models.CharField(max_length=64, default=_token, db_index=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=80, blank=True, default="site")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email


# ==========================================
# Merged from projects/models.py
# ==========================================

"""Projects = the portfolio, the core marketing asset (architecture §2.2)."""


class ProjectCategory(models.Model):
    key = models.SlugField(max_length=60, unique=True)
    label = models.CharField(max_length=120)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "label"]
        verbose_name_plural = "Project categories"

    def __str__(self) -> str:
        return self.label


class Project(PublishableModel):
    slug = models.SlugField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    category = models.ForeignKey(
        ProjectCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="projects",
    )
    type = models.CharField(max_length=120, blank=True)
    status_label = models.CharField(
        max_length=120, blank=True, help_text="e.g. Completed, In progress"
    )
    excerpt = models.CharField(max_length=400, blank=True)
    description = models.TextField(blank=True)
    services = models.JSONField(
        default=list, blank=True, help_text="Service tags for this project"
    )

    cover = models.ForeignKey(
        "core.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    is_featured = models.BooleanField(default=False)
    featured_order = models.PositiveIntegerField(default=0)

    seo = GenericRelation("core.SeoMeta")

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["category", "status"]),
            models.Index(
                fields=["featured_order"],
                name="proj_featured_idx",
                condition=models.Q(is_featured=True),
            ),
        ]

    def __str__(self) -> str:
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="gallery"
    )
    media = models.ForeignKey("core.Media", on_delete=models.CASCADE, related_name="+")
    caption = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.project.slug} image #{self.sort_order}"


# ==========================================
# Merged from seo/models.py
# ==========================================

"""Polymorphic SEO metadata (architecture §2.2 / §9).

Attaches to any content object via a generic FK, or to an ad-hoc route via
`path` (for pages that aren't backed by a model). Owns title/description,
canonical, Open Graph, Twitter Card and a JSON-LD schema blob.
"""


class SeoMeta(models.Model):
    class TwitterCard(models.TextChoices):
        SUMMARY = "summary", "Summary"
        SUMMARY_LARGE = "summary_large_image", "Summary large image"

    # Either attach to an object (generic FK) ...
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # ... or to a bare path (e.g. "/contact").
    path = models.CharField(
        max_length=512, null=True, blank=True, unique=True, db_index=True
    )

    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    canonical_url = models.URLField(blank=True)
    og_title = models.CharField(max_length=180, blank=True)
    og_description = models.CharField(max_length=320, blank=True)
    og_image = models.ForeignKey(
        "core.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    twitter_card = models.CharField(
        max_length=20, choices=TwitterCard.choices, default=TwitterCard.SUMMARY_LARGE
    )
    robots_directives = models.CharField(
        max_length=120, blank=True, default="index,follow"
    )
    schema_jsonld = models.JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SEO metadata"
        verbose_name_plural = "SEO metadata"
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id"],
                name="uniq_seo_per_object",
                condition=models.Q(object_id__isnull=False),
            )
        ]

    def __str__(self) -> str:
        return self.path or self.meta_title or f"SEO #{self.pk}"


# ==========================================
# Merged from team/models.py
# ==========================================


class TeamMember(PublishableModel):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ForeignKey(
        "core.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


# ==========================================
# Merged from testimonials/models.py
# ==========================================


class Testimonial(PublishableModel):
    author_name = models.CharField(max_length=200)
    author_role = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    avatar = models.ForeignKey(
        "core.Media",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__isnull=True)
                | models.Q(rating__gte=1, rating__lte=5),
                name="testimonial_rating_range",
            )
        ]

    def __str__(self) -> str:
        return f"{self.author_name}"


# ==========================================
# Merged from users/models.py
# ==========================================

"""Custom email-login user with role-based access (architecture §5)."""


class Role(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    ADMIN = "admin", "Admin"
    EDITOR = "editor", "Editor"
    CONTENT_MANAGER = "content_manager", "Content Manager"
    SEO_MANAGER = "seo_manager", "SEO Manager"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email: str, password: str, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", Role.SUPER_ADMIN)
        if extra.get("is_staff") is not True or extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")
        return self._create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CONTENT_MANAGER
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    mfa_enabled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return self.full_name or self.email

    def get_short_name(self) -> str:
        return self.full_name.split(" ")[0] if self.full_name else self.email

    # --- Role helpers used by permission classes ---
    @property
    def is_super_admin(self) -> bool:
        return self.role == Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_admin_level(self) -> bool:
        return self.is_super_admin or self.role == Role.ADMIN

    def can_publish(self) -> bool:
        return self.is_admin_level or self.role == Role.EDITOR

    def manages_seo(self) -> bool:
        return self.is_admin_level or self.role == Role.SEO_MANAGER
