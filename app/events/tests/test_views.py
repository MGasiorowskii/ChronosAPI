import pytest
import pytz

from datetime import datetime
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

from events.models import CalendarEvent, ConferenceRoom

EVENTS_ENDPOINT_V1 = "v1:calendar-events"
LOCATION_ENDPOINT_V1 = "v1:conference-rooms"

START_EVENT = datetime(2024, 11, 21, 16, 16, 1, tzinfo=pytz.utc)
END_EVENT = datetime(2024, 11, 21, 18, 20, 2, tzinfo=pytz.utc)
DT_FORMAT = "%Y-%m-%dT%H:%M:%S%:z"

pytestmark = pytest.mark.django_db


@pytest.fixture
def event_data():
    return dict(
        event_name="Test Event",
        agenda="Test Agenda",
        start=START_EVENT.strftime(DT_FORMAT),
        end=END_EVENT.strftime(DT_FORMAT),
        participants=[],
    )


@pytest.mark.parametrize("endpoint", [EVENTS_ENDPOINT_V1, LOCATION_ENDPOINT_V1])
def test_list_view_api_response_with_200(user_client, endpoint):
    url = reverse(f"{endpoint}-list")
    response = user_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_retrieve_single_conference_room(user_client, conference_room):
    endpoint = f"{LOCATION_ENDPOINT_V1}-detail"
    url = reverse(endpoint, args=(conference_room.id,))
    response = user_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == conference_room.id


def test_retrieve_single_calendar_event_room(user_client, calendar_event):
    endpoint = f"{EVENTS_ENDPOINT_V1}-detail"
    url = reverse(endpoint, args=(calendar_event.id,))
    response = user_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == calendar_event.id


def test_create_conference_room(user_client, user):
    url = reverse(f"{LOCATION_ENDPOINT_V1}-list")
    data = {"name": "Test Room", "address": "Test Address", "manager": user.id}

    response = user_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert ConferenceRoom.objects.filter(id=response.data["id"]).exists()
    assert response.data["name"] == data["name"]
    assert response.data["address"] == data["address"]
    assert response.data["manager"] == user.id


def test_create_calendar_event(
    user_client, conference_room, participants, user, event_data
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    participant_emails = [p.email for p in participants]
    event_data.update(
        {
            "location": conference_room.id,
            "participants": participant_emails,
        }
    )

    response = user_client.post(url, data=event_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert CalendarEvent.objects.filter(id=response.data["id"]).exists()
    assert response.data["owner"] == user.email
    assert response.data["event_name"] == event_data["event_name"]
    assert response.data["agenda"] == event_data["agenda"]
    assert response.data["location"] == conference_room.address
    assert list(response.data["participants"]) == participant_emails
    assert response.data["start"] == event_data["start"].replace("+00:00", "Z")
    assert response.data["end"] == event_data["end"].replace("+00:00", "Z")


def test_create_calendar_event_without_participants_and_location(
    user_client, user, event_data
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")

    response = user_client.post(url, data=event_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert CalendarEvent.objects.filter(id=response.data["id"]).exists()
    assert response.data["owner"] == user.email
    assert response.data["event_name"] == event_data["event_name"]
    assert response.data["agenda"] == event_data["agenda"]
    assert response.data["location"] == None
    assert list(response.data["participants"]) == []
    assert response.data["start"] == event_data["start"].replace("+00:00", "Z")
    assert response.data["end"] == event_data["end"].replace("+00:00", "Z")


def test_num_of_queries_on_calendar_events_list(
    django_assert_num_queries,
    user_client,
    calendar_events,
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    with django_assert_num_queries(2):
        """
        SELECT DISTINCT "events_calendarevent"
        SELECT "events_calendarevent_participants" (prefetch_related)
        """
        user_client.get(url)


def test_num_of_queries_on_conference_rooms_list(
    django_assert_num_queries,
    user_client,
    calendar_events,
):
    baker.make("events.ConferenceRoom", _quantity=3)
    url = reverse(f"{LOCATION_ENDPOINT_V1}-list")

    with django_assert_num_queries(1):
        """
        SELECT "events_conferenceroom"
        """
        user_client.get(url)


def test_list_calendar_events_is_timezone_aware(
    client, different_timezone_user, calendar_event
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    tz = pytz.timezone("Australia/Sydney")
    expected_start_date = calendar_event.start.astimezone(tz).strftime(
        "%Y-%m-%dT%H:%M:%S%:z"
    )
    expected_end_date = calendar_event.end.astimezone(tz).strftime(
        "%Y-%m-%dT%H:%M:%S%:z"
    )

    client.force_authenticate(user=different_timezone_user)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == calendar_event.id
    assert response.data[0]["start"] == expected_start_date
    assert response.data[0]["end"] == expected_end_date


def test_create_calendar_events_is_timezone_aware(
    client, different_timezone_user, event_data
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    tz = pytz.timezone(different_timezone_user.timezone)

    event_data["start"] = START_EVENT.astimezone(tz).strftime(DT_FORMAT)
    event_data["end"] = END_EVENT.astimezone(tz).strftime(DT_FORMAT)

    client.force_authenticate(user=different_timezone_user)
    response = client.post(url, data=event_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    event = CalendarEvent.objects.get(id=response.data["id"])
    assert event.start == START_EVENT
    assert event.end == END_EVENT


def test_calendar_events_filter_by_day_is_timezone_aware(
    client, different_timezone_user, calendar_events
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")

    tz = pytz.timezone(different_timezone_user.timezone)
    day = calendar_events[0].start.astimezone(tz).strftime("%Y-%m-%d")

    client.force_authenticate(user=different_timezone_user)
    response = client.get(url, {"day": day})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == calendar_events[0].id


def test_calendar_events_filter_by_location_id(user_client, calendar_events):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    location_id = calendar_events[0].location_id
    response = user_client.get(url, {"location_id": location_id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == calendar_events[0].id


@pytest.mark.parametrize("attribute", ["event_name", "agenda"])
def test_calendar_events_filter_by_name_or_agenda(
    user_client, calendar_events, attribute
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    query = getattr(calendar_events[0], attribute)
    response = user_client.get(url, {"query": query})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == calendar_events[0].id


@pytest.mark.parametrize(
    "query, expected_count",
    [("event 1", 1), ("agenda 1", 1), ("event", 4), ("agenda", 4)],
)
def test_calendar_events_filter_by_name_or_agenda_is_case_insensitive(
    user_client, calendar_events, expected_count, query
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    response = user_client.get(url, {"query": query})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == expected_count


def test_calendar_events_filter_by_day(user_client, calendar_events):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    day = calendar_events[0].start.strftime("%Y-%m-%d")
    response = user_client.get(url, {"day": day})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == calendar_events[0].id


def test_calendar_events_cant_be_longer_than_8_hours(user_client, user, event_data):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    event_data.update(
        {
            "start": "2024-11-21T12:00:00Z",
            "end": "2024-11-21T20:00:01Z",
        }
    )

    response = user_client.post(url, data=event_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["time"] == [
        ErrorDetail(
            string="The meeting duration cannot be longer than 8 hours.", code="invalid"
        )
    ]


def test_calendar_events_start_have_to_be_earlier_than_stop(
    user_client, user, event_data
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    event_data.update(
        {
            "start": "2024-11-21T12:00:00Z",
            "end": "2024-11-21T11:59:59Z",
        }
    )

    response = user_client.post(url, data=event_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["time"] == [
        ErrorDetail(
            string="The start time must be earlier than the end time.", code="invalid"
        )
    ]


def test_calendar_events_are_visibly_only_for_owner_participants_and_location_manager(
    client, calendar_event
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")

    client.force_authenticate(user=calendar_event.location.manager)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["id"] == calendar_event.id

    unauthorized_user = baker.make("accounts.User")
    client.force_authenticate(user=unauthorized_user)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0

    client.force_authenticate(user=calendar_event.participants.first())
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["id"] == calendar_event.id

    client.force_authenticate(user=calendar_event.owner)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["id"] == calendar_event.id


def test_calendar_events_are_not_visibly_for_external_users(
    external_user_client, calendar_event
):
    url = reverse(f"{EVENTS_ENDPOINT_V1}-list")
    response = external_user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


def test_conference_rooms_are_not_visibly_for_external_users(
    external_user_client, conference_room
):
    url = reverse(f"{LOCATION_ENDPOINT_V1}-list")
    response = external_user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
