from __future__ import annotations

from .models import AuditLog
from .models import BlogCategory, BlogPost, Tag
from .models import JobApplication, JobOpening
from .models import Lead, LeadNote
from .models import Office, Page, HeroSlide, RedirectRule, SiteSetting, Stat
from .models import Project, ProjectCategory, ProjectImage
from .models import SeoMeta
from .models import Subscriber
from .models import TeamMember
from .models import Testimonial
from .models import User, NotificationSetting
from apps.core.models import Media
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.html import format_html


# ==========================================
# Merged from core/admin.py
# ==========================================


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("city", "country", "phone", "sort_order")
    list_editable = ("sort_order",)
    search_fields = ("city", "country")


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "updated_at")
    search_fields = ("key",)


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "suffix", "sort_order")
    list_editable = ("sort_order",)
    search_fields = ("label",)


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ("email",)
    
    def has_add_permission(self, request):
        # We only want one singleton settings object
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False



@admin.register(RedirectRule)
class RedirectRuleAdmin(admin.ModelAdmin):
    list_display = ("from_path", "to_path", "status_code", "is_active")
    list_filter = ("status_code", "is_active")
    search_fields = ("from_path", "to_path")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("key", "title")
    prepopulated_fields = {"key": ("title",)}


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "image", "sort_order", "is_active", "created_at")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)
    autocomplete_fields = ("image",)


# ==========================================
# Merged from seo/admin.py
# ==========================================


@admin.register(SeoMeta)
class SeoMetaAdmin(admin.ModelAdmin):
    """Standalone SEO workspace — create/manage path-based entries (e.g. /contact,
    /studio) directly, plus see object-attached meta. Object-bound rows are also
    editable inline on their content admin via SeoMetaInline."""

    list_display = ("__str__", "path", "meta_title", "robots_directives", "updated_at")
    list_filter = ("twitter_card", "robots_directives")
    search_fields = ("path", "meta_title", "meta_description", "canonical_url")
    fields = (
        "path",
        "content_type",
        "object_id",
        "meta_title",
        "meta_description",
        "canonical_url",
        "og_title",
        "og_description",
        "og_image",
        "twitter_card",
        "robots_directives",
        "schema_jsonld",
    )
    autocomplete_fields = ("og_image",)


class SeoMetaInline(GenericStackedInline):
    """Attach to any content ModelAdmin to edit its SEO inline."""

    model = SeoMeta
    extra = 0
    max_num = 1
    fields = (
        "meta_title",
        "meta_description",
        "canonical_url",
        "og_title",
        "og_description",
        "og_image",
        "twitter_card",
        "robots_directives",
        "schema_jsonld",
    )


# ==========================================
# Merged from audit/admin.py
# ==========================================


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "actor",
        "target_type",
        "target_id",
        "ip_address",
    )
    list_filter = ("action", "target_type", "created_at")
    search_fields = ("target_type", "target_id", "actor__email", "ip_address")
    date_hierarchy = "created_at"
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return request.user.is_superuser


# ==========================================
# Merged from blog/admin.py
# ==========================================


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "slug")
    prepopulated_fields = {"slug": ("label",)}
    search_fields = ("label",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("label", "slug")
    prepopulated_fields = {"slug": ("label",)}
    search_fields = ("label",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "author",
        "status",
        "published_at",
        "reading_minutes",
    )
    list_filter = ("status", "category", "tags")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("cover", "category", "author")
    filter_horizontal = ("tags",)
    date_hierarchy = "published_at"
    inlines = [SeoMetaInline]


# ==========================================
# Merged from careers/admin.py
# ==========================================


@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "place",
        "employment_type",
        "is_open",
        "status",
        "closes_at",
    )
    list_filter = ("status", "is_open", "employment_type")
    search_fields = ("title", "place")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """Applications are records, not editable content. Only the pipeline
    status and assignee may be changed."""

    list_display = (
        "full_name",
        "email",
        "applying_for",
        "opening",
        "status",
        "assigned_to",
        "created_at",
    )
    list_filter = ("status", "opening", "created_at")
    search_fields = ("first_name", "last_name", "email", "applying_for")
    autocomplete_fields = ("assigned_to",)
    date_hierarchy = "created_at"
    readonly_fields = (
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
        "cv_link",
        "portfolio_link",
        "cover_letter_link",
        "terms_accepted",
        "terms_accepted_at",
        "source",
        "ip_address",
        "user_agent",
        "created_at",
    )
    fields = ("status", "assigned_to", *readonly_fields)

    @admin.display(description="Name")
    def full_name(self, obj: JobApplication) -> str:
        return f"{obj.first_name} {obj.last_name}"

    def _file_link(self, media, label):
        if not media:
            return "—"
        return format_html(
            '<span title="Download via admin API signed URL">{} (private)</span>', label
        )

    @admin.display(description="CV")
    def cv_link(self, obj):
        return self._file_link(obj.cv, "CV")

    @admin.display(description="Portfolio")
    def portfolio_link(self, obj):
        return self._file_link(obj.portfolio, "Portfolio")

    @admin.display(description="Cover letter")
    def cover_letter_link(self, obj):
        return self._file_link(obj.cover_letter, "Cover letter")

    def has_add_permission(self, request) -> bool:
        return False


# ==========================================
# Merged from leads/admin.py
# ==========================================


class LeadNoteInline(admin.TabularInline):
    model = LeadNote
    extra = 1
    readonly_fields = ("author", "created_at")

    def save_model(self, request, obj, form, change):  # pragma: no cover
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "status", "source", "assigned_to", "created_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("name", "email", "phone", "message")
    autocomplete_fields = ("assigned_to",)
    date_hierarchy = "created_at"
    inlines = [LeadNoteInline]
    readonly_fields = (
        "name",
        "email",
        "phone",
        "message",
        "source",
        "spam_score",
        "ip_address",
        "user_agent",
        "created_at",
        "updated_at",
    )
    fields = ("status", "assigned_to", *readonly_fields)

    def has_add_permission(self, request) -> bool:
        # Leads are system-generated by the contact form.
        return False

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, LeadNote) and not instance.author_id:
                instance.author = request.user
            instance.save()
        formset.save_m2m()


# ==========================================
# Merged from media/admin.py
# ==========================================


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("original_name", "type", "is_private", "created_at")
    list_filter = ("type", "is_private", "created_at")
    search_fields = ("original_name", "alt_text")


# ==========================================
# Merged from newsletter/admin.py
# ==========================================


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "status", "source", "confirmed_at", "created_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("email",)
    readonly_fields = (
        "confirm_token",
        "confirmed_at",
        "unsubscribed_at",
        "ip_address",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False


# ==========================================
# Merged from projects/admin.py
# ==========================================


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "key", "sort_order")
    list_editable = ("sort_order",)
    prepopulated_fields = {"key": ("label",)}
    autocomplete_fields = ("image",)
    search_fields = ("label", "blurb")


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    autocomplete_fields = ("media",)
    fields = ("media", "caption", "sort_order")
    ordering = ("sort_order",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "year",
        "status",
        "is_featured",
        "featured_order",
        "published_at",
    )
    list_filter = ("status", "category", "is_featured", "year")
    list_editable = ("is_featured", "featured_order")
    search_fields = ("title", "location", "excerpt", "description")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("cover",)
    date_hierarchy = "published_at"
    inlines = [ProjectImageInline, SeoMetaInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "type", "status_label")}),
        (
            "Details",
            {"fields": ("location", "year", "excerpt", "description", "services")},
        ),
        ("Media & feature", {"fields": ("cover", "is_featured", "featured_order")}),
        ("Publishing", {"fields": ("status", "published_at")}),
    )


# ==========================================
# Merged from team/admin.py
# ==========================================


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "status", "sort_order")
    list_editable = ("sort_order",)
    list_filter = ("status",)
    search_fields = ("name", "role")
    autocomplete_fields = ("photo",)


# ==========================================
# Merged from testimonials/admin.py
# ==========================================


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "company", "rating", "status", "sort_order")
    list_editable = ("sort_order",)
    list_filter = ("status", "rating")
    search_fields = ("author_name", "company", "quote")
    autocomplete_fields = ("avatar",)


# ==========================================
# Merged from users/admin.py
# ==========================================


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ("email", "full_name", "role")


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm
    model = User

    ordering = ("email",)
    list_display = (
        "email",
        "full_name",
        "role",
        "is_active",
        "is_staff",
        "mfa_enabled",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "full_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("full_name", "role", "mfa_enabled")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    readonly_fields = ("last_login", "created_at")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "role", "password1", "password2"),
            },
        ),
    )
