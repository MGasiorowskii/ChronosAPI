from rest_framework import serializers
from pytz import timezone


class TimeZoneDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if request := self.context.get("request"):
            self.timezone = timezone(request.user.timezone)
        return super().to_representation(value)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if request := self.context.get("request"):
            self.timezone = timezone(request.user.timezone)
        return value
