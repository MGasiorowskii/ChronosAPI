from datetime import timedelta

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.utils import TimeZoneDateTimeField
from accounts.models import User
from events.models import ConferenceRoom, CalendarEvent


MAX_MEETING_DURATION_HOURS = 8


class ConferenceRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceRoom
        fields = ["id", "name", "address", "manager"]


class CalendarEventSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.email")
    participants = serializers.ListSerializer(child=serializers.EmailField())
    start = TimeZoneDateTimeField()
    end = TimeZoneDateTimeField()

    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "owner",
            "event_name",
            "agenda",
            "start",
            "end",
            "location",
            "participants",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["location"] = instance.location.address if instance.location else None
        data["participants"] = [p.email for p in instance.participants.all()]
        return data

    def validate(self, data):
        errors = {}
        errors.update(self.validate_time(data))

        if errors:
            raise ValidationError(errors)

        return data

    def validate_time(self, data):
        start = data.get("start")
        end = data.get("end")

        if start and end:
            if start >= end:
                return {"time": "The start time must be earlier than the end time."}
            elif end - start > timedelta(hours=MAX_MEETING_DURATION_HOURS):
                return {"time": "The meeting duration cannot be longer than 8 hours."}
        return {}

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        validated_data["participants"] = User.objects.filter(
            email__in=validated_data["participants"],
            company_id=self.context["request"].user.company_id,
        )
        return super().create(validated_data)
