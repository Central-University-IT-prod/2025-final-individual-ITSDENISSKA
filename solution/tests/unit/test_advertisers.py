import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.main import app
from uuid import UUID

client = TestClient(app)


@pytest.fixture
def sample_advertiser():
    return {
        "advertiser_id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Test Advertiser",
    }


@pytest.fixture
def invalid_advertiser():
    return {"advertiser_id": "invalid-uuid", "name": "Invalid Advertiser"}


def test_create_advertiser(sample_advertiser):
    response = client.post("/advertisers/bulk", json=[sample_advertiser])
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == sample_advertiser["name"]


def test_create_advertiser_invalid_data(invalid_advertiser):
    response = client.post("/advertisers/bulk", json=[invalid_advertiser])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_advertiser(sample_advertiser):
    client.post("/advertisers/bulk", json=[sample_advertiser])

    advertiser_id = sample_advertiser["advertiser_id"]
    response = client.get(f"/advertisers/{advertiser_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == sample_advertiser["name"]


def test_get_advertiser_not_found():
    response = client.get("/advertisers/00000000-0000-0000-0000-000000000000")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Advertiser not found"}
