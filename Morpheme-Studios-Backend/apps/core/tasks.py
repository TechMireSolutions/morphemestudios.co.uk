from __future__ import annotations

import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def notify_new_application(self, application_id: int) -> None:
    from .models import JobApplication, NotificationSetting

    try:
        app = JobApplication.objects.get(pk=application_id)
    except JobApplication.DoesNotExist:
        return
        
    notify_email = NotificationSetting.load().email
    subject = f"New job application: {app.first_name} {app.last_name}"
    
    cv_url = app.cv.file.url if app.cv else "None"
    portfolio_url = app.portfolio.file.url if app.portfolio else "None"
    cover_letter_url = app.cover_letter.file.url if app.cover_letter else "None"
    
    body = (
        f"A new application was received.\n\n"
        f"--- Applicant PII ---\n"
        f"Name: {app.first_name} {app.last_name}\n"
        f"Email: {app.email}\n"
        f"Phone: {app.phone or '-'}\n"
        f"Gender: {app.gender or '-'}\n"
        f"Date of Birth: {app.date_of_birth or '-'}\n"
        f"Nationality: {app.nationality or '-'}\n"
        f"Country of Residence: {app.country_of_residence or '-'}\n"
        f"Home Address: {app.home_address or '-'}\n\n"
        f"--- Application Details ---\n"
        f"Applying for: {app.applying_for or (app.opening.title if app.opening else 'Speculative')}\n"
        f"Field of Expertise: {app.field_of_expertise or '-'}\n"
        f"Education: {app.education or '-'}\n"
        f"Experience Range: {app.experience_range or '-'}\n\n"
        f"--- Uploaded Documents ---\n"
        f"CV: {settings.API_URL}{cv_url}\n"
        f"Portfolio: {settings.API_URL}{portfolio_url}\n"
        f"Cover Letter: {settings.API_URL}{cover_letter_url}\n\n"
        f"Review in admin: {settings.API_URL}/admin/careers/jobapplication/{app.id}/change/"
    )
    try:
        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [notify_email]
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Application notification email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def notify_new_lead(self, lead_id: int) -> None:
    from .models import Lead, NotificationSetting

    try:
        lead = Lead.objects.get(pk=lead_id)
    except Lead.DoesNotExist:
        return
        
    notify_email = NotificationSetting.load().email
    subject = f"New enquiry from {lead.name}"
    
    body = (
        f"A new contact form submission was received.\n\n"
        f"Name: {lead.name}\n"
        f"Email: {lead.email}\n"
        f"Phone: {lead.phone or '-'}\n"
        f"Source: {lead.source}\n"
        f"IP Address: {lead.ip_address}\n"
        f"User Agent: {lead.user_agent}\n\n"
        f"Message:\n{lead.message}\n\n"
        f"Manage: {settings.API_URL}/admin/leads/lead/{lead.id}/change/"
    )
    try:
        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [notify_email]
        )
    except Exception as exc:  # noqa: BLE001 - retry transient SMTP failures
        logger.warning("Lead notification email failed (will retry): %s", exc)
        raise self.retry(exc=exc)


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
