from datetime import datetime

import pytz
from django.db.models import Q
from django.db.models.functions import TruncDate
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin

from events.models import CalendarEvent, ConferenceRoom
from events.serializers.v1 import CalendarEventSerializer, ConferenceRoomSerializer


class BaseViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]


class ConferenceRoomViewSet(BaseViewSet):
    queryset = ConferenceRoom.objects.all()
    serializer_class = ConferenceRoomSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(manager__company_id=self.request.user.company_id)


class CalendarEventViewSet(BaseViewSet):
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return (
            queryset.filter(owner__company_id=self.request.user.company_id)
            .select_related("location", "owner")
            .prefetch_related("participants")
        ).distinct()

    def filter_queryset(self, queryset):
        queryset = self.filter_by_scope(queryset)
        queryset = self.filter_by_query(queryset)
        queryset = self.filter_by_day(queryset)
        queryset = self.filter_by_location(queryset)
        return super().filter_queryset(queryset)

    def filter_by_scope(self, queryset):
        user = self.request.user
        return queryset.filter(
            Q(owner=user) | Q(participants=user) | Q(location__manager=user)
        )

    def filter_by_query(self, queryset):
        if query := self.request.query_params.get("query"):
            queryset = queryset.filter(
                Q(event_name__icontains=query) | Q(agenda__icontains=query)
            )
        return queryset

    def filter_by_day(self, queryset):
        if day := self.request.query_params.get("day"):
            user_tz = pytz.timezone(self.request.user.timezone)
            queryset = (
                queryset.annotate(
                    tz_start=TruncDate("start", tzinfo=user_tz),
                    tz_end=TruncDate("end", tzinfo=user_tz),
                )
                .filter(Q(tz_start=day) | Q(tz_end=day)))
        return queryset

    def filter_by_location(self, queryset):
        if location_id := self.request.query_params.get("location_id"):
            queryset = queryset.filter(location_id=location_id)
        return queryset
