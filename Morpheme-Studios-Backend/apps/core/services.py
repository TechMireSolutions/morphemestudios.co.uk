from __future__ import annotations

from .middleware import current_context
from .models import AuditLog
from .models import SeoMeta
from apps.core.models import Media
from django.conf import settings


# ==========================================
# Merged from core/services.py
# ==========================================


# === audit/services.py ===

"""Single entry point for writing audit entries."""


def record(
    action: str,
    *,
    target=None,
    target_type: str = "",
    target_id: str = "",
    changes: dict | None = None,
) -> AuditLog:
    ctx = current_context()
    if target is not None:
        target_type = target_type or target.__class__.__name__
        target_id = target_id or str(getattr(target, "pk", ""))
    return AuditLog.objects.create(
        actor=ctx["actor"],
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        changes=changes or {},
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
    )


# === media/services.py ===


def store_private_upload(file_obj) -> Media:
    media = Media.objects.create(
        type=Media.Type.DOCUMENT,
        is_private=True,
        original_name=file_obj.name,
        file=file_obj,
    )
    return media


# === seo/services.py ===

"""Build the SEO payload for a route: resolved metadata + JSON-LD, with sane
auto-fallbacks when an editor hasn't set explicit values (architecture Â§9)."""


def _abs(path: str) -> str:
    return f"{settings.SITE_URL.rstrip('/')}{path}"


def organization_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Morpheme Studios",
        "url": settings.SITE_URL,
    }


def meta_for_path(path: str, obj=None, *, defaults: dict | None = None) -> dict:
    """Resolve SeoMeta for a path or attached object, falling back to defaults."""
    defaults = defaults or {}
    meta = None
    if obj is not None:
        meta = SeoMeta.objects.filter(
            content_type__model=obj._meta.model_name,
            object_id=obj.pk,
        ).first()
    if meta is None:
        meta = SeoMeta.objects.filter(path=path).first()

    title = (
        meta.meta_title
        if meta and meta.meta_title
        else defaults.get("title", "Morpheme Studios")
    )
    description = (
        meta.meta_description
        if meta and meta.meta_description
        else defaults.get("description", "")
    )
    canonical = meta.canonical_url if meta and meta.canonical_url else _abs(path)
    og_image = None
    if meta and meta.og_image and not meta.og_image.is_private:
        try:
            og_image = meta.og_image.file.url
        except ValueError:
            og_image = None
    og_image = og_image or defaults.get("og_image")

    schema = (
        meta.schema_jsonld if meta and meta.schema_jsonld else defaults.get("schema")
    )

    return {
        "path": path,
        "title": title,
        "description": description,
        "canonical": canonical,
        "robots": (meta.robots_directives if meta else "index,follow"),
        "og": {
            "title": (meta.og_title if meta and meta.og_title else title),
            "description": (
                meta.og_description if meta and meta.og_description else description
            ),
            "image": og_image,
        },
        "twitter_card": (meta.twitter_card if meta else "summary_large_image"),
        "jsonld": schema or organization_schema(),
    }


# ==========================================
# Merged from audit/services.py
# ==========================================

"""Single entry point for writing audit entries."""


def record(
    action: str,
    *,
    target=None,
    target_type: str = "",
    target_id: str = "",
    changes: dict | None = None,
) -> AuditLog:
    ctx = current_context()
    if target is not None:
        target_type = target_type or target.__class__.__name__
        target_id = target_id or str(getattr(target, "pk", ""))
    return AuditLog.objects.create(
        actor=ctx["actor"],
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        changes=changes or {},
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
    )


# ==========================================
# Merged from media/services.py
# ==========================================


def store_private_upload(file_obj) -> Media:
    media = Media.objects.create(
        type=Media.Type.DOCUMENT,
        is_private=True,
        original_name=file_obj.name,
        file=file_obj,
    )
    return media


# ==========================================
# Merged from seo/services.py
# ==========================================

"""Build the SEO payload for a route: resolved metadata + JSON-LD, with sane
auto-fallbacks when an editor hasn't set explicit values (architecture §9)."""


def _abs(path: str) -> str:
    return f"{settings.SITE_URL.rstrip('/')}{path}"


def organization_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Morpheme Studios",
        "url": settings.SITE_URL,
    }


def meta_for_path(path: str, obj=None, *, defaults: dict | None = None) -> dict:
    """Resolve SeoMeta for a path or attached object, falling back to defaults."""
    defaults = defaults or {}
    meta = None
    if obj is not None:
        meta = SeoMeta.objects.filter(
            content_type__model=obj._meta.model_name,
            object_id=obj.pk,
        ).first()
    if meta is None:
        meta = SeoMeta.objects.filter(path=path).first()

    title = (
        meta.meta_title
        if meta and meta.meta_title
        else defaults.get("title", "Morpheme Studios")
    )
    description = (
        meta.meta_description
        if meta and meta.meta_description
        else defaults.get("description", "")
    )
    canonical = meta.canonical_url if meta and meta.canonical_url else _abs(path)
    og_image = None
    if meta and meta.og_image and not meta.og_image.is_private:
        try:
            og_image = meta.og_image.file.url
        except ValueError:
            og_image = None
    og_image = og_image or defaults.get("og_image")

    schema = (
        meta.schema_jsonld if meta and meta.schema_jsonld else defaults.get("schema")
    )

    return {
        "path": path,
        "title": title,
        "description": description,
        "canonical": canonical,
        "robots": (meta.robots_directives if meta else "index,follow"),
        "og": {
            "title": (meta.og_title if meta and meta.og_title else title),
            "description": (
                meta.og_description if meta and meta.og_description else description
            ),
            "image": og_image,
        },
        "twitter_card": (meta.twitter_card if meta else "summary_large_image"),
        "jsonld": schema or organization_schema(),
    }
