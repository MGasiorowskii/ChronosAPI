from django.contrib import admin

from events.models import ConferenceRoom, CalendarEvent


@admin.register(ConferenceRoom)
class ConferenceRoom(admin.ModelAdmin):
    list_display = ("name", "manager", "address")


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = (
        "event_name",
        "owner",
        "start",
        "end",
        "location",
        "agenda",
        "get_participants",
    )

    def get_participants(self, obj):
        return ", ".join([str(participant) for participant in obj.participants.all()])

    get_participants.short_description = "Participants"
