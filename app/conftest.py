import pytest

from model_bakery import baker
from rest_framework.test import APIClient

USER_COMPANY_UUID = "342245a4-4539-49ac-86d4-be2c9cb05253"
EXTERNAL_USER_COMPANY_UUID = "f6443e0a-1f29-4aa9-96f0-76db16104414"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return baker.make(
        "accounts.User",
        username="User 1",
        email="user1@compnayA.com",
        timezone="UTC",
        company_id=USER_COMPANY_UUID,
    )


@pytest.fixture
def different_timezone_user():
    return baker.make(
        "accounts.User",
        username="TZ User",
        email="tz.user@compnayA.com",
        timezone="Australia/Sydney",
        company_id=USER_COMPANY_UUID,
    )


@pytest.fixture
def external_user():
    return baker.make(
        "accounts.User",
        username="External User",
        email="external.user@compnayB.com",
        timezone="UTC",
        company_id=EXTERNAL_USER_COMPANY_UUID,
    )


@pytest.fixture
def user_client(user, client):
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def external_user_client(external_user, client):
    client.force_authenticate(user=external_user)
    return client
