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
        "location": "NYC",
        "gender": "MALE",
    }


@pytest.fixture
def sample_advertiser():
    return {
        "advertiser_id": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Test Advertiser",
    }


@pytest.fixture
def sample_ml_score(sample_client, sample_advertiser):
    client.post("/clients/bulk", json=[sample_client])
    client.post("/advertisers/bulk", json=[sample_advertiser])
    return {
        "client_id": sample_client["client_id"],
        "advertiser_id": sample_advertiser["advertiser_id"],
        "score": 85,
    }


@pytest.fixture
def invalid_ml_score():
    return {
        "client_id": "invalid-client-id",
        "advertiser_id": "invalid-advertiser-id",
        "score": -1.5,
    }


def test_add_new_ml_score(sample_ml_score):
    response = client.post("/ml-scores", json=sample_ml_score)
    assert response.status_code == status.HTTP_200_OK


def test_update_existing_ml_score(sample_ml_score):
    client.post("/ml-scores", json=sample_ml_score)
    updated_score = sample_ml_score.copy()
    updated_score["score"] = 95
    response = client.post("/ml-scores", json=updated_score)
    assert response.status_code == status.HTTP_200_OK


def test_add_invalid_ml_score(invalid_ml_score):
    response = client.post("/ml-scores", json=invalid_ml_score)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_add_ml_score_with_nonexistent_client_or_advertiser(sample_ml_score):
    invalid_client_score = sample_ml_score.copy()
    invalid_client_score["client_id"] = "00000000-0000-0000-0000-000000000000"
    response = client.post("/ml-scores", json=invalid_client_score)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    invalid_advertiser_score = sample_ml_score.copy()
    invalid_advertiser_score["advertiser_id"] = "00000000-0000-0000-0000-000000000000"
    response = client.post("/ml-scores", json=invalid_advertiser_score)
    assert response.status_code == status.HTTP_404_NOT_FOUND
