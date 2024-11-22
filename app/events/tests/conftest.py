from datetime import datetime, timedelta

import pytest
import pytz
from model_bakery import baker

from conftest import USER_COMPANY_UUID


START_EVENT = datetime(2024, 11, 21, 16, 16, 1, tzinfo=pytz.utc)
END_EVENT = datetime(2024, 11, 21, 18, 20, 2, tzinfo=pytz.utc)


@pytest.fixture
def conference_room(user):
    return baker.make(
        "events.ConferenceRoom",
        name="Fixture Room",
        address="Fixture Address",
        manager=user,
    )


@pytest.fixture
def participants():
    emails = ["user2@compnayA.com", "user3@compnayA.com", "user4@compnayA.com"]
    usernames = [email.split("@")[0].title() for email in emails]
    return baker.make(
        "accounts.User",
        _quantity=len(emails),
        company_id=USER_COMPANY_UUID,
        timezone="UTC",
        username=iter(usernames),
        email=iter(emails),
    )


@pytest.fixture
def calendar_event(user, participants, conference_room, different_timezone_user):
    participants.append(different_timezone_user)
    return baker.make(
        "events.CalendarEvent",
        event_name="Fixture Event",
        agenda="Fixture Agenda",
        owner=user,
        participants=participants,
        location=conference_room,
        start=START_EVENT,
        end=END_EVENT,
    )


@pytest.fixture
def calendar_events(user, participants, different_timezone_user):
    locations = baker.make("events.ConferenceRoom", _quantity=4)
    participants.append(different_timezone_user)
    events = []
    for i in range(4):
        event = baker.make(
            "events.CalendarEvent",
            event_name=f"Event {i}",
            agenda=f"Agenda {i}",
            owner=user,
            participants=participants[i:],
            location=locations[i],
            start=START_EVENT + timedelta(days=i),
            end=END_EVENT + timedelta(days=i),
        )
        events.append(event)

    return events
