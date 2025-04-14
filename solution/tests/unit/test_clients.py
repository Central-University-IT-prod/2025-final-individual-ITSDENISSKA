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
def invalid_client():
    return {
        "client_id": "invalid-uuid",
        "login": "invalid@user",
        "age": -1,
        "location": "NYC",
        "gender": "INVALID",
    }


def test_create_client(sample_client):
    response = client.post("/clients/bulk", json=[sample_client])
    assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.json()}"
    data = response.json()
    assert len(data) == 1
    assert data[0]["login"] == sample_client["login"]


def test_create_client_invalid_data(invalid_client):
    response = client.post("/clients/bulk", json=[invalid_client])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_client(sample_client):
    response = client.post("/clients/bulk", json=[sample_client])
    assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.json()}"
    clients = response.json()
    client_id = clients[0]["client_id"]

    response = client.get(f"/clients/{client_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["login"] == sample_client["login"]


def test_get_client_not_found():
    response = client.get("/clients/00000000-0000-0000-0000-000000000000")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Client not found"}
