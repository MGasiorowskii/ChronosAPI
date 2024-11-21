import uuid
import pytz

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    company_id = models.UUIDField(default=uuid.uuid4, blank=False, null=False)
    timezone = models.CharField(
        max_length=50, choices=[(tz, tz) for tz in pytz.all_timezones], default="UTC"
    )
