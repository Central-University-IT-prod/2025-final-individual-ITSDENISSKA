import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.main import app
from uuid import UUID

client = TestClient(app)


@pytest.fixture
def sample_campaign():
    return {
        "impressions_limit": 100,
        "clicks_limit": 50,
        "cost_per_impression": 0.1,
        "cost_per_click": 0.5,
        "ad_title": "Test Campaign",
        "ad_text": "Sample text",
        "start_date": 1672531200,
        "end_date": 1675209600,
        "targeting": {
            "gender": "MALE",
            "age_from": 18,
            "age_to": 35,
            "location": "USA",
        },
    }


@pytest.fixture
def invalid_campaign():
    return {
        "impressions_limit": -100,
        "clicks_limit": 50,
        "cost_per_impression": 0.1,
        "cost_per_click": 0.5,
        "ad_title": "Invalid Campaign",
        "ad_text": "Sample text",
        "start_date": 1672531200,
        "end_date": 1675209600,
        "targeting": {
            "gender": "INVALID",
            "age_from": 18,
            "age_to": 35,
            "location": "USA",
        },
    }


@pytest.fixture
def sample_advertiser():
    return {
        "advertiser_id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Test Advertiser",
    }


def test_create_campaign(sample_advertiser, sample_campaign):
    client.post("/advertisers/bulk", json=[sample_advertiser])

    advertiser_id = sample_advertiser["advertiser_id"]
    response = client.post(
        f"/advertisers/{advertiser_id}/campaigns", json=sample_campaign
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["ad_title"] == sample_campaign["ad_title"]


def test_create_campaign_invalid_data(sample_advertiser, invalid_campaign):
    client.post("/advertisers/bulk", json=[sample_advertiser])

    advertiser_id = sample_advertiser["advertiser_id"]
    response = client.post(
        f"/advertisers/{advertiser_id}/campaigns", json=invalid_campaign
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_campaign(sample_advertiser, sample_campaign):
    response = client.post("/advertisers/bulk", json=[sample_advertiser])
    advertiser_id = sample_advertiser["advertiser_id"]

    response = client.post(
        f"/advertisers/{advertiser_id}/campaigns", json=sample_campaign
    )
    assert response.status_code == status.HTTP_201_CREATED
    campaign_data = response.json()
    campaign_id = campaign_data["campaign_id"]

    response = client.get(f"/advertisers/{advertiser_id}/campaigns/{campaign_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["ad_title"] == sample_campaign["ad_title"]


def test_get_campaign_not_found(sample_advertiser):
    advertiser_id = sample_advertiser["advertiser_id"]
    response = client.get(
        f"/advertisers/{advertiser_id}/campaigns/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Campaign not found"}


def test_delete_campaign(sample_advertiser, sample_campaign):
    client.post("/advertisers/bulk", json=[sample_advertiser])
    advertiser_id = sample_advertiser["advertiser_id"]
    response = client.post(
        f"/advertisers/{advertiser_id}/campaigns", json=sample_campaign
    )
    campaign_id = response.json()["campaign_id"]

    response = client.delete(f"/advertisers/{advertiser_id}/campaigns/{campaign_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get(f"/advertisers/{advertiser_id}/campaigns/{campaign_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
