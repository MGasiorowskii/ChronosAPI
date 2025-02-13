# Generated by Django 5.1.3 on 2024-11-21 14:31

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_alter_calendarevent_location"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="calendarevent",
            name="participants",
            field=models.ManyToManyField(
                blank=True,
                related_name="participating_events",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
