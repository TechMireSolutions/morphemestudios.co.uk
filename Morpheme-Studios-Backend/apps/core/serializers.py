from __future__ import annotations

from .models import BlogCategory, BlogPost, Tag
from .models import JobApplication, JobOpening
from .models import Lead
from .models import Office, Page
from .models import Project, ProjectCategory, ProjectImage
from .models import TeamMember
from .models import Testimonial
from .models import User
from apps.core.models import Media
from apps.core.services import store_private_upload
from apps.core.turnstile import verify_turnstile
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = [
            "id",
            "type",
            "is_private",
            "original_name",
            "alt_text",
            "file",
            "created_at",
        ]


# ==========================================
# Merged from newsletter/serializers.py
# ==========================================



# ==========================================
# Merged from core/serializers.py
# ==========================================


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = (
            "id",
            "city",
            "country",
            "address_lines",
            "phone",
            "email",
            "latitude",
            "longitude",
            "sort_order",
        )


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("key", "title", "blocks", "updated_at")


# ==========================================
# Merged from blog/serializers.py
# ==========================================


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ("slug", "label")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("slug", "label")


class BlogPostListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    tags = serializers.SlugRelatedField(slug_field="slug", many=True, read_only=True)
    cover = MediaSerializer()
    author = serializers.CharField(
        source="author.get_full_name", default="", read_only=True
    )

    class Meta:
        model = BlogPost
        fields = (
            "slug",
            "title",
            "excerpt",
            "cover",
            "category",
            "tags",
            "author",
            "reading_minutes",
            "published_at",
        )


class BlogPostDetailSerializer(BlogPostListSerializer):
    class Meta(BlogPostListSerializer.Meta):
        fields = BlogPostListSerializer.Meta.fields + ("body",)


# ==========================================
# Merged from careers/serializers.py
# ==========================================


class JobOpeningListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOpening
        fields = ("slug", "title", "place", "employment_type", "is_open", "closes_at")


class JobOpeningDetailSerializer(JobOpeningListSerializer):
    class Meta(JobOpeningListSerializer.Meta):
        fields = JobOpeningListSerializer.Meta.fields + ("description", "requirements")


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    cv = serializers.FileField(write_only=True)
    portfolio = serializers.FileField(write_only=True, required=False, allow_null=True)
    cover_letter = serializers.FileField(
        write_only=True, required=False, allow_null=True
    )
    turnstile_token = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = JobApplication
        fields = (
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
            "terms_accepted",
            "cv",
            "portfolio",
            "cover_letter",
            "turnstile_token",
        )

    def validate_terms_accepted(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError("You must accept the terms to apply.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        ip = request.META.get("REMOTE_ADDR") if request else None
        if not verify_turnstile(attrs.get("turnstile_token"), ip):
            raise serializers.ValidationError({"turnstile_token": "Spam check failed."})
        return attrs

    def create(self, validated):
        request = self.context.get("request")
        actor = getattr(request, "user", None)
        files = {k: validated.pop(k, None) for k in ("cv", "portfolio", "cover_letter")}
        validated.pop("turnstile_token", None)

        media_refs = {}
        try:
            for key, f in files.items():
                if f is not None:
                    media_refs[key] = store_private_upload(f, uploaded_by=actor)
        except DjangoValidationError as exc:
            # Surface file errors as field errors.
            raise serializers.ValidationError({"cv": exc.messages}) from exc

        application = JobApplication.objects.create(
            **validated,
            cv=media_refs.get("cv"),
            portfolio=media_refs.get("portfolio"),
            cover_letter=media_refs.get("cover_letter"),
            terms_accepted_at=timezone.now(),
            source="careers_form",
            ip_address=request.META.get("REMOTE_ADDR") if request else None,
            user_agent=(
                request.META.get("HTTP_USER_AGENT", "")[:512] if request else ""
            ),
        )
        return application

    def to_representation(self, instance):
        return {"id": instance.id, "status": "received"}


# ==========================================
# Merged from leads/serializers.py
# ==========================================


class LeadCreateSerializer(serializers.ModelSerializer):
    turnstile_token = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    # Honeypot: bots fill hidden fields; humans never do.
    company_website = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = Lead
        fields = (
            "name",
            "email",
            "phone",
            "message",
            "turnstile_token",
            "company_website",
        )

    def validate(self, attrs):
        if attrs.get("company_website"):
            raise serializers.ValidationError("Spam detected.")
        request = self.context.get("request")
        ip = request.META.get("REMOTE_ADDR") if request else None
        if not verify_turnstile(attrs.get("turnstile_token"), ip):
            raise serializers.ValidationError({"turnstile_token": "Spam check failed."})
        return attrs

    def create(self, validated):
        validated.pop("turnstile_token", None)
        validated.pop("company_website", None)
        request = self.context.get("request")
        return Lead.objects.create(
            **validated,
            source="contact_form",
            ip_address=request.META.get("REMOTE_ADDR") if request else None,
            user_agent=(
                request.META.get("HTTP_USER_AGENT", "")[:512] if request else ""
            ),
        )

    def to_representation(self, instance):
        return {"id": instance.id, "status": "received"}


# ==========================================
# Merged from media/serializers.py
# ==========================================



class SubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    turnstile_token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        request = self.context.get("request")
        ip = request.META.get("REMOTE_ADDR") if request else None
        if not verify_turnstile(attrs.get("turnstile_token"), ip):
            raise serializers.ValidationError({"turnstile_token": "Spam check failed."})
        return attrs


class UnsubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("token"):
            raise serializers.ValidationError("Provide an email or token.")
        return attrs


# ==========================================
# Merged from projects/serializers.py
# ==========================================


class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ("key", "label", "sort_order")


class ProjectImageSerializer(serializers.ModelSerializer):
    media = MediaSerializer()

    class Meta:
        model = ProjectImage
        fields = ("media", "caption", "sort_order")


class ProjectListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="key", read_only=True)
    cover = MediaSerializer()

    class Meta:
        model = Project
        fields = (
            "slug",
            "title",
            "location",
            "year",
            "category",
            "type",
            "status_label",
            "excerpt",
            "services",
            "cover",
            "is_featured",
        )


class ProjectDetailSerializer(ProjectListSerializer):
    gallery = ProjectImageSerializer(many=True, read_only=True)

    class Meta(ProjectListSerializer.Meta):
        fields = ProjectListSerializer.Meta.fields + (
            "description",
            "gallery",
            "published_at",
        )


# ==========================================
# Merged from team/serializers.py
# ==========================================


class TeamMemberSerializer(serializers.ModelSerializer):
    photo = MediaSerializer()

    class Meta:
        model = TeamMember
        fields = ("id", "name", "role", "bio", "photo", "sort_order")


# ==========================================
# Merged from testimonials/serializers.py
# ==========================================


class TestimonialSerializer(serializers.ModelSerializer):
    avatar = MediaSerializer()

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
        )


# ==========================================
# Merged from users/serializers.py
# ==========================================


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "role",
            "is_staff",
            "mfa_enabled",
            "last_login",
        )
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=12)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=12)
