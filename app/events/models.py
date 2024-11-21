from django.db import models
from django.conf import settings


class ConferenceRoom(models.Model):
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="managed_rooms",
        null=True,
    )
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)


class CalendarEvent(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_events"
    )
    event_name = models.CharField(max_length=255)
    agenda = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="participating_events", blank=True
    )
    location = models.ForeignKey(
        ConferenceRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
