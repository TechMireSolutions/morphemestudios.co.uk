from __future__ import annotations

# === core/middleware.py ===

"""Runtime redirects driven by the editable RedirectRule table (architecture §9).

Matches the incoming path against active rules and issues a 301/302 before the
view runs — so editors can fix old WordPress URLs without code/Nginx changes.
Rules are cached briefly to avoid a DB hit on every request, and app routes
(api/admin/media) are skipped so redirects never shadow the application.
"""


from django.core.cache import cache
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

_CACHE_KEY = "core:redirect_rules"
_CACHE_TTL = 60  # seconds


def _rules() -> dict[str, tuple[str, int]]:
    rules = cache.get(_CACHE_KEY)
    if rules is None:
        from apps.core.models import RedirectRule

        rules = {
            r.from_path: (r.to_path, r.status_code)
            for r in RedirectRule.objects.filter(is_active=True).only(
                "from_path", "to_path", "status_code"
            )
        }
        cache.set(_CACHE_KEY, rules, _CACHE_TTL)
    return rules


class RedirectMiddleware:
    SKIP_PREFIXES = ("/admin", "/api", "/media", "/static", "/protected", "/_protected")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not path.startswith(self.SKIP_PREFIXES):
            rules = _rules()
            match = (
                rules.get(path) or rules.get(path.rstrip("/")) or rules.get(path + "/")
            )
            if match:
                to_path, code = match
                cls = (
                    HttpResponsePermanentRedirect
                    if code == 301
                    else HttpResponseRedirect
                )
                return cls(to_path)
        return self.get_response(request)


# === audit/middleware.py ===

"""Stashes the current request's actor/IP/UA in a thread-local so the audit
service can attribute mutations without threading `request` everywhere."""

import threading

_ctx = threading.local()


def get_client_ip(request) -> str | None:
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _ctx.actor = getattr(request, "user", None)
        _ctx.ip = get_client_ip(request)
        _ctx.user_agent = request.META.get("HTTP_USER_AGENT", "")[:512]
        try:
            return self.get_response(request)
        finally:
            _ctx.actor = None
            _ctx.ip = None
            _ctx.user_agent = ""


def current_context() -> dict:
    actor = getattr(_ctx, "actor", None)
    if actor is not None and not getattr(actor, "is_authenticated", False):
        actor = None
    return {
        "actor": actor,
        "ip_address": getattr(_ctx, "ip", None),
        "user_agent": getattr(_ctx, "user_agent", ""),
    }
