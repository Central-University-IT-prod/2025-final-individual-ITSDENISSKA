import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.main import app
from uuid import UUID

client = TestClient(app)


@pytest.fixture
def sample_client():
    return {
        "client_id": "123e4567-e89b-12d3-a456-426614174000",
        "login": "test_user",
        "age": 25,
        "location": "test_location_ad_show",
        "gender": "MALE",
    }


@pytest.fixture
def sample_advertiser():
    return {
        "advertiser_id": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Test Advertiser",
    }


@pytest.fixture
def sample_campaign(sample_advertiser):
    return {
        "impressions_limit": 100,
        "clicks_limit": 50,
        "cost_per_impression": 0.1,
        "cost_per_click": 0.5,
        "ad_title": "Test Campaign",
        "ad_text": "Sample text",
        "start_date": 1,
        "end_date": 7,
        "targeting": {
            "gender": "ALL",
            "age_from": 18,
            "age_to": 35,
            "location": "test_location_ad_show",
        },
    }


def test_show_ad_to_client(sample_client, sample_advertiser, sample_campaign):
    response = client.post("/clients/bulk", json=[sample_client])
    assert response.status_code == status.HTTP_201_CREATED

    response = client.post("/advertisers/bulk", json=[sample_advertiser])
    assert response.status_code == status.HTTP_201_CREATED

    advertiser_id = sample_advertiser["advertiser_id"]
    response = client.post(
        f"/advertisers/{advertiser_id}/campaigns", json=sample_campaign
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = client.post("/time/advance", json={"current_date": 1})
    assert response.status_code == status.HTTP_200_OK

    client_id = sample_client["client_id"]
    response = client.get(f"/ads?client_id={client_id}")
    assert response.status_code == status.HTTP_200_OK
    ad_response = response.json()
    assert ad_response["advertiser_id"] == advertiser_id


def test_click_on_ad(sample_client, sample_advertiser, sample_campaign):
    client.post("/clients/bulk", json=[sample_client])
    advertiser_id = sample_advertiser["advertiser_id"]
    client.post("/advertisers/bulk", json=[sample_advertiser])
    client.post(f"/advertisers/{advertiser_id}/campaigns", json=sample_campaign)

    client.post("/time/advance", json={"current_date": 1})

    client_id = sample_client["client_id"]
    ad_response = client.get(f"/ads?client_id={client_id}").json()

    response = client.post(
        f"/ads/{ad_response['ad_id']}/click", json={"client_id": client_id}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
