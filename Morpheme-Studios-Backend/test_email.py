import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.models import Lead, NotificationSetting

print(NotificationSetting.load().email)

lead, _ = Lead.objects.get_or_create(
    name="Test User",
    email="test@example.com",
    message="This is a test message"
)

from apps.core.tasks import notify_new_lead
notify_new_lead(lead.id)

print("Lead notification executed successfully!")
