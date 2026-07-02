from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import logging


# ==========================================
# Merged from core/tasks.py
# ==========================================


# ==========================================
# Merged from core/tasks.py
# ==========================================


# ==========================================
# Merged from careers/tasks.py
# ==========================================

"""Background tasks for careers (run by the Celery worker; eager in dev/tests)."""


logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def notify_new_application(self, application_id: int) -> None:
    from .models import JobApplication

    try:
        app = JobApplication.objects.get(pk=application_id)
    except JobApplication.DoesNotExist:
        return
    subject = f"New job application: {app.first_name} {app.last_name}"
    body = (
        f"A new application was received.\n\n"
        f"Name: {app.first_name} {app.last_name}\n"
        f"Email: {app.email}\n"
        f"Applying for: {app.applying_for or (app.opening.title if app.opening else 'Speculative')}\n"
        f"Review in admin: {settings.API_URL}/admin/careers/jobapplication/{app.id}/change/"
    )
    try:
        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [settings.LEADS_NOTIFY_EMAIL]
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Application notification email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


# ==========================================
# Merged from leads/tasks.py
# ==========================================

"""Background tasks for leads (run by the Celery worker; eager in dev/tests)."""


logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def notify_new_lead(self, lead_id: int) -> None:
    from .models import Lead

    try:
        lead = Lead.objects.get(pk=lead_id)
    except Lead.DoesNotExist:
        return
    subject = f"New enquiry from {lead.name}"
    body = (
        f"Name: {lead.name}\nEmail: {lead.email}\nPhone: {lead.phone or '-'}\n\n"
        f"Message:\n{lead.message}\n\n"
        f"Manage: {settings.API_URL}/admin/leads/lead/{lead.id}/change/"
    )
    try:
        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [settings.LEADS_NOTIFY_EMAIL]
        )
    except Exception as exc:  # noqa: BLE001 - retry transient SMTP failures
        logger.warning("Lead notification email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


# ==========================================
# Merged from newsletter/tasks.py
# ==========================================

"""Background tasks for newsletter (run by the Celery worker; eager in dev/tests)."""


logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def send_confirmation_email(self, subscriber_id: int) -> None:
    from .models import Subscriber

    try:
        sub = Subscriber.objects.get(pk=subscriber_id)
    except Subscriber.DoesNotExist:
        return
    # Idempotency: only the pending state needs a confirmation email. If a retry
    # or duplicate delivery fires after the user already confirmed/unsubscribed,
    # do nothing.
    if sub.status != Subscriber.Status.PENDING:
        return
    confirm_url = f"{settings.SITE_URL}/newsletter/confirm?token={sub.confirm_token}"
    try:
        send_mail(
            "Confirm your subscription",
            f"Please confirm your subscription to Morpheme Studios:\n\n{confirm_url}\n",
            settings.DEFAULT_FROM_EMAIL,
            [sub.email],
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Newsletter confirmation email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


# ==========================================
# Merged from careers/tasks.py
# ==========================================

"""Background tasks for careers (run by the Celery worker; eager in dev/tests)."""


logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def notify_new_application(self, application_id: int) -> None:
    from .models import JobApplication

    try:
        app = JobApplication.objects.get(pk=application_id)
    except JobApplication.DoesNotExist:
        return
    subject = f"New job application: {app.first_name} {app.last_name}"
    body = (
        f"A new application was received.\n\n"
        f"Name: {app.first_name} {app.last_name}\n"
        f"Email: {app.email}\n"
        f"Applying for: {app.applying_for or (app.opening.title if app.opening else 'Speculative')}\n"
        f"Review in admin: {settings.API_URL}/admin/careers/jobapplication/{app.id}/change/"
    )
    try:
        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [settings.LEADS_NOTIFY_EMAIL]
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Application notification email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


# ==========================================
# Merged from leads/tasks.py
# ==========================================

"""Background tasks for leads (run by the Celery worker; eager in dev/tests)."""


logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def notify_new_lead(self, lead_id: int) -> None:
    from .models import Lead

    try:
        lead = Lead.objects.get(pk=lead_id)
    except Lead.DoesNotExist:
        return
    subject = f"New enquiry from {lead.name}"
    body = (
        f"Name: {lead.name}\nEmail: {lead.email}\nPhone: {lead.phone or '-'}\n\n"
        f"Message:\n{lead.message}\n\n"
        f"Manage: {settings.API_URL}/admin/leads/lead/{lead.id}/change/"
    )
    try:
        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [settings.LEADS_NOTIFY_EMAIL]
        )
    except Exception as exc:  # noqa: BLE001 - retry transient SMTP failures
        logger.warning("Lead notification email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


# ==========================================
# Merged from newsletter/tasks.py
# ==========================================

"""Background tasks for newsletter (run by the Celery worker; eager in dev/tests)."""


logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def send_confirmation_email(self, subscriber_id: int) -> None:
    from .models import Subscriber

    try:
        sub = Subscriber.objects.get(pk=subscriber_id)
    except Subscriber.DoesNotExist:
        return
    # Idempotency: only the pending state needs a confirmation email. If a retry
    # or duplicate delivery fires after the user already confirmed/unsubscribed,
    # do nothing.
    if sub.status != Subscriber.Status.PENDING:
        return
    confirm_url = f"{settings.SITE_URL}/newsletter/confirm?token={sub.confirm_token}"
    try:
        send_mail(
            "Confirm your subscription",
            f"Please confirm your subscription to Morpheme Studios:\n\n{confirm_url}\n",
            settings.DEFAULT_FROM_EMAIL,
            [sub.email],
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Newsletter confirmation email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


# ==========================================
# Merged from careers/tasks.py
# ==========================================

"""Background tasks for careers (run by the Celery worker; eager in dev/tests)."""


logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def notify_new_application(self, application_id: int) -> None:
    from .models import JobApplication

    try:
        app = JobApplication.objects.get(pk=application_id)
    except JobApplication.DoesNotExist:
        return
    subject = f"New job application: {app.first_name} {app.last_name}"
    body = (
        f"A new application was received.\n\n"
        f"Name: {app.first_name} {app.last_name}\n"
        f"Email: {app.email}\n"
        f"Applying for: {app.applying_for or (app.opening.title if app.opening else 'Speculative')}\n"
        f"Review in admin: {settings.API_URL}/admin/careers/jobapplication/{app.id}/change/"
    )
    try:
        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [settings.LEADS_NOTIFY_EMAIL]
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Application notification email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


# ==========================================
# Merged from leads/tasks.py
# ==========================================

"""Background tasks for leads (run by the Celery worker; eager in dev/tests)."""


logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def notify_new_lead(self, lead_id: int) -> None:
    from .models import Lead

    try:
        lead = Lead.objects.get(pk=lead_id)
    except Lead.DoesNotExist:
        return
    subject = f"New enquiry from {lead.name}"
    body = (
        f"Name: {lead.name}\nEmail: {lead.email}\nPhone: {lead.phone or '-'}\n\n"
        f"Message:\n{lead.message}\n\n"
        f"Manage: {settings.API_URL}/admin/leads/lead/{lead.id}/change/"
    )
    try:
        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [settings.LEADS_NOTIFY_EMAIL]
        )
    except Exception as exc:  # noqa: BLE001 - retry transient SMTP failures
        logger.warning("Lead notification email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


# ==========================================
# Merged from newsletter/tasks.py
# ==========================================

"""Background tasks for newsletter (run by the Celery worker; eager in dev/tests)."""


logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def send_confirmation_email(self, subscriber_id: int) -> None:
    from .models import Subscriber

    try:
        sub = Subscriber.objects.get(pk=subscriber_id)
    except Subscriber.DoesNotExist:
        return
    # Idempotency: only the pending state needs a confirmation email. If a retry
    # or duplicate delivery fires after the user already confirmed/unsubscribed,
    # do nothing.
    if sub.status != Subscriber.Status.PENDING:
        return
    confirm_url = f"{settings.SITE_URL}/newsletter/confirm?token={sub.confirm_token}"
    try:
        send_mail(
            "Confirm your subscription",
            f"Please confirm your subscription to Morpheme Studios:\n\n{confirm_url}\n",
            settings.DEFAULT_FROM_EMAIL,
            [sub.email],
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Newsletter confirmation email failed (will retry): %s", exc)
        raise self.retry(exc=exc)
