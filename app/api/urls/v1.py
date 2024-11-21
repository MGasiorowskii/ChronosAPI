from django.urls import include, path
from rest_framework.routers import DefaultRouter

from events.views.v1 import ConferenceRoomViewSet, CalendarEventViewSet

router = DefaultRouter()

router.register(r"conference-rooms", ConferenceRoomViewSet)
router.register(r"calendar-events", CalendarEventViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
