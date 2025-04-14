import json
import uuid
from copy import copy

from fastapi import status
from fastapi.testclient import TestClient
from src.main import app
from uuid import UUID

client = TestClient(app)

test_client_data = {
    "client_id": str(uuid.uuid4()),
    "login": "test_user",
    "age": 30,
    "location": "test_location_1",
    "gender": "MALE",
}


bulk_clients_data = [
    {
        "client_id": str(uuid.uuid4()),
        "login": "user1",
        "age": 25,
        "location": "test_location_1",
        "gender": "FEMALE",
    },
    {
        "client_id": str(uuid.uuid4()),
        "login": "user2",
        "age": 40,
        "location": "test_location_1",
        "gender": "MALE",
    },
]


def test_create_single_client():
    response = client.post("/clients/bulk", json=[test_client_data])
    assert response.status_code == status.HTTP_201_CREATED
    created_client = response.json()[0]
    assert UUID(created_client["client_id"]) == UUID(test_client_data["client_id"])
    assert created_client["login"] == test_client_data["login"]
    assert created_client["age"] == test_client_data["age"]
    assert created_client["location"] == test_client_data["location"]
    assert created_client["gender"] == test_client_data["gender"]


def test_create_bulk_clients():
    response = client.post("/clients/bulk", json=bulk_clients_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_clients = response.json()
    assert len(created_clients) == len(bulk_clients_data)
    for created_client in bulk_clients_data:
        response = client.get(f"clients/{created_client['client_id']}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == created_client


def test_create_client_with_incorrect_client_id():
    incorrect_clint_id_user = {
        "client_id": 1,
        "login": "test_user",
        "age": 30,
        "location": "test_location_1",
        "gender": "MALE",
    }
    response = client.post("/clients/bulk", json=[incorrect_clint_id_user])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_client_with_incorrect_age():
    incorrect_age_user = {
        "client_id": str(uuid.uuid4()),
        "login": "test_user",
        "age": -1,
        "location": "test_location_1",
        "gender": "MALE",
    }
    response = client.post("/clients/bulk", json=[incorrect_age_user])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_client_with_incorrect_gender():
    incorrect_gender_user = {
        "client_id": str(uuid.uuid4()),
        "login": "test_user",
        "age": 30,
        "location": "test_location_1",
        "gender": "BI",
    }
    response = client.post("/clients/bulk", json=[incorrect_gender_user])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_client_with_incorrect_login():
    incorrect_gender_user = {
        "client_id": str(uuid.uuid4()),
        "login": "!!!!",
        "age": 30,
        "location": "test_location_1",
        "gender": "BI",
    }
    response = client.post("/clients/bulk", json=[incorrect_gender_user])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_location_client():
    response = client.get(f"/clients/{test_client_data['client_id']}")
    assert response.status_code == status.HTTP_200_OK
    client_data = response.json()
    updated_data = copy(client_data)
    updated_data["location"] = "test_update_location_1"
    response = client.post("/clients/bulk", json=[updated_data])
    assert response.status_code == status.HTTP_201_CREATED
    updated_client = response.json()[0]
    assert (
        updated_client["client_id"]
        == updated_data["client_id"]
        == client_data["client_id"]
    )
    assert (
        updated_client["location"]
        == updated_data["location"]
        != client_data["location"]
    )
    client.post("/clients/bulk", json=[test_client_data])


def test_update_login_client():
    response = client.get(f"/clients/{test_client_data['client_id']}")
    assert response.status_code == status.HTTP_200_OK
    client_data = response.json()
    updated_data = copy(client_data)
    updated_data["login"] = "test_update_login_1"
    response = client.post("/clients/bulk", json=[updated_data])
    assert response.status_code == status.HTTP_201_CREATED
    updated_client = response.json()[0]
    assert (
        updated_client["client_id"]
        == test_client_data["client_id"]
        == client_data["client_id"]
    )
    assert updated_client["login"] == updated_data["login"] != client_data["login"]
    client.post("/clients/bulk", json=[test_client_data])


def test_update_age_client():
    response = client.get(f"/clients/{test_client_data['client_id']}")
    assert response.status_code == status.HTTP_200_OK
    client_data = response.json()
    updated_data = copy(client_data)
    updated_data["age"] = 40
    response = client.post("/clients/bulk", json=[updated_data])
    assert response.status_code == status.HTTP_201_CREATED
    updated_client = response.json()[0]
    assert (
        updated_client["client_id"]
        == test_client_data["client_id"]
        == client_data["client_id"]
    )
    assert updated_client["age"] == updated_data["age"] != client_data["age"]
    client.post("/clients/bulk", json=[test_client_data])


def test_update_gender_client():
    response = client.get(f"/clients/{test_client_data['client_id']}")
    assert response.status_code == status.HTTP_200_OK
    client_data = response.json()
    updated_data = copy(client_data)
    updated_data["gender"] = "FEMALE"
    response = client.post("/clients/bulk", json=[updated_data])
    assert response.status_code == status.HTTP_201_CREATED
    updated_client = response.json()[0]
    assert (
        updated_client["client_id"]
        == test_client_data["client_id"]
        == client_data["client_id"]
    )
    assert updated_client["gender"] == updated_data["gender"] != client_data["gender"]
    client.post("/clients/bulk", json=[test_client_data])


test_advertiser_data = {
    "advertiser_id": str(uuid.uuid4()),
    "name": "Test Advertiser",
}

bulk_advertisers_data = [
    {"advertiser_id": str(uuid.uuid4()), "name": "Advertiser 1"},
    {"advertiser_id": str(uuid.uuid4()), "name": "Advertiser 2"},
]


def test_create_bulk_advertisers():
    response = client.post("/advertisers/bulk", json=bulk_advertisers_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_advertisers = response.json()
    assert len(created_advertisers) == len(bulk_advertisers_data)
    for created_advertiser in created_advertisers:
        advertiser_id = created_advertiser["advertiser_id"]
        assert UUID(advertiser_id)
        matching_advertiser = next(
            (
                adv
                for adv in bulk_advertisers_data
                if adv["advertiser_id"] == advertiser_id
            ),
            None,
        )
        assert matching_advertiser is not None
        assert created_advertiser["name"] == matching_advertiser["name"]


def test_get_advertiser_by_id():
    response = client.post("/advertisers/bulk", json=[test_advertiser_data])
    assert response.status_code == status.HTTP_201_CREATED
    created_advertiser = response.json()[0]
    advertiser_id = created_advertiser["advertiser_id"]
    response = client.get(f"/advertisers/{advertiser_id}")
    assert response.status_code == status.HTTP_200_OK
    retrieved_advertiser = response.json()
    assert retrieved_advertiser["advertiser_id"] == advertiser_id
    assert retrieved_advertiser["name"] == test_advertiser_data["name"]


def test_get_advertiser_by_nonexistent_id():
    nonexistent_id = str(uuid.uuid4())
    response = client.get(f"/advertisers/{nonexistent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_advertiser_with_invalid_advertiser_id():
    invalid_advertiser_data = {
        "advertiser_id": 1,
        "name": "Invalid Advertiser",
    }
    response = client.post("/advertisers/bulk", json=[invalid_advertiser_data])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_advertiser_with_invalid_name():
    invalid_advertiser_data = {
        "advertiser_id": str(uuid.uuid4()),
        "name": "",
    }
    response = client.post("/advertisers/bulk", json=[invalid_advertiser_data])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_advertiser_name():
    response = client.post("/advertisers/bulk", json=[test_advertiser_data])
    assert response.status_code == status.HTTP_201_CREATED
    created_advertiser = response.json()[0]
    advertiser_id = created_advertiser["advertiser_id"]
    updated_data = {"advertiser_id": advertiser_id, "name": "Updated Advertiser Name"}
    response = client.post("/advertisers/bulk", json=[updated_data])
    assert response.status_code == status.HTTP_201_CREATED
    updated_advertiser = response.json()[0]
    assert updated_advertiser["advertiser_id"] == advertiser_id
    assert updated_advertiser["name"] == updated_data["name"]


test_campaign_data = {
    "impressions_limit": 1000,
    "clicks_limit": 500,
    "cost_per_impression": 0.01,
    "cost_per_click": 0.1,
    "ad_title": "Test Campaign Ad",
    "ad_text": "This is a test campaign ad.",
    "start_date": 1,
    "end_date": 10,
    "targeting": {
        "gender": "ALL",
        "age_from": 18,
        "age_to": 50,
        "location": "Test Location",
    },
}


def test_create_single_campaign():
    response = client.post(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns",
        json=test_campaign_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_campaign = response.json()
    assert created_campaign["ad_title"] == test_campaign_data["ad_title"]
    assert created_campaign["ad_text"] == test_campaign_data["ad_text"]
    assert (
        created_campaign["impressions_limit"] == test_campaign_data["impressions_limit"]
    )
    assert created_campaign["clicks_limit"] == test_campaign_data["clicks_limit"]


def test_create_campaign_with_invalid_advertiser_id():
    invalid_advertiser_id = "invalid_id"
    response = client.post(
        f"/advertisers/{invalid_advertiser_id}/campaigns", json=test_campaign_data
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_campaign_with_invalid_start_date():
    invalid_campaign_data = test_campaign_data.copy()
    invalid_campaign_data["start_date"] = -1
    response = client.post(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns",
        json=invalid_campaign_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_campaign_with_invalid_end_date():
    invalid_campaign_data = test_campaign_data.copy()
    invalid_campaign_data["end_date"] = -1
    response = client.post(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns",
        json=invalid_campaign_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_campaign():
    create_response = client.post(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns",
        json=test_campaign_data,
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    created_campaign = create_response.json()

    updated_data = {
        "ad_title": "Updated Campaign Title",
        "ad_text": "This is an updated campaign ad.",
        "cost_per_impression": 0.015,
        "cost_per_click": 0.15,
    }
    update_response = client.put(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns/{created_campaign['campaign_id']}",
        json=updated_data,
    )
    assert update_response.status_code == status.HTTP_200_OK
    updated_campaign = update_response.json()
    assert updated_campaign["ad_title"] == updated_data["ad_title"]
    assert updated_campaign["ad_text"] == updated_data["ad_text"]
    assert (
        updated_campaign["cost_per_impression"] == updated_data["cost_per_impression"]
    )


def test_delete_campaign():
    create_response = client.post(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns",
        json=test_campaign_data,
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    created_campaign = create_response.json()

    delete_response = client.delete(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns/{created_campaign['campaign_id']}"
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns/{created_campaign['campaign_id']}"
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_get_campaign_by_id():
    create_response = client.post(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns",
        json=test_campaign_data,
    )
    assert (
        create_response.status_code == status.HTTP_201_CREATED
    ), create_response.json()
    created_campaign = create_response.json()

    get_response = client.get(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns/{created_campaign['campaign_id']}"
    )
    assert get_response.status_code == status.HTTP_200_OK
    retrieved_campaign = get_response.json()
    assert retrieved_campaign["ad_title"] == test_campaign_data["ad_title"]
    assert retrieved_campaign["ad_text"] == test_campaign_data["ad_text"]


def test_get_campaign_by_nonexistent_id():
    nonexistent_id = str(uuid.uuid4())
    response = client.get(
        f"/advertisers/{test_advertiser_data['advertiser_id']}/campaigns/{nonexistent_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


test_clients_data = [
    {
        "client_id": str(uuid.uuid4()),
        "login": f"user_{i}",
        "age": 20 + i,
        "location": f"location_{i}",
        "gender": "MALE" if i % 2 == 0 else "FEMALE",
    }
    for i in range(10)
]

test_advertisers_data = [
    {
        "advertiser_id": str(uuid.uuid4()),
        "name": f"Advertiser_{i}",
    }
    for i in range(10)
]


def test_create_bulk_clients_for_test_ad():
    response = client.post("/clients/bulk", json=test_clients_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_clients = response.json()
    assert len(created_clients) == len(test_clients_data)
    for created_client in created_clients:
        assert UUID(created_client["client_id"])
        matching_client = next(
            (
                c
                for c in test_clients_data
                if c["client_id"] == created_client["client_id"]
            ),
            None,
        )
        assert matching_client is not None
        assert created_client["login"] == matching_client["login"]
        assert created_client["age"] == matching_client["age"]
        assert created_client["location"] == matching_client["location"]
        assert created_client["gender"] == matching_client["gender"]


def test_create_bulk_advertisers_for_test_ad():
    response = client.post("/advertisers/bulk", json=test_advertisers_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_advertisers = response.json()
    assert len(created_advertisers) == len(test_advertisers_data)
    for created_advertiser in created_advertisers:
        assert UUID(created_advertiser["advertiser_id"])
        matching_advertiser = next(
            (
                adv
                for adv in test_advertisers_data
                if adv["advertiser_id"] == created_advertiser["advertiser_id"]
            ),
            None,
        )
        assert matching_advertiser is not None
        assert created_advertiser["name"] == matching_advertiser["name"]


def test_add_ml_scores():
    for client_data in test_clients_data:
        for advertiser_data in test_advertisers_data:
            ml_score_payload = {
                "client_id": client_data["client_id"],
                "advertiser_id": advertiser_data["advertiser_id"],
                "score": int((client_data["age"] + len(advertiser_data["name"])) % 100),
            }
            response = client.post("/ml-scores", json=ml_score_payload)
            assert response.status_code == status.HTTP_200_OK


test_ads_data = []
for advertiser in test_advertisers_data:
    for i in range(10):
        test_ads_data.append(
            {
                "impressions_limit": 1000,
                "clicks_limit": 500,
                "cost_per_impression": 0.01,
                "cost_per_click": 0.1,
                "ad_title": f"Ad Title {i}",
                "ad_text": f"Ad Text {i}",
                "start_date": 1,
                "end_date": 10,
                "targeting": {
                    "gender": (
                        "ALL" if i % 2 == 0 else ("MALE" if i % 3 == 0 else "FEMALE")
                    ),
                    "age_from": 18 + (i * 2),
                    "age_to": 50 - (i * 2),
                    "location": f"location_{i % 10}",
                },
                "advertiser_id": advertiser["advertiser_id"],
            }
        )


def add_ml_scores():
    for client_data in test_clients_data:
        for advertiser_data in test_advertisers_data:
            ml_score_payload = {
                "client_id": client_data["client_id"],
                "advertiser_id": advertiser_data["advertiser_id"],
                "score": int((client_data["age"] + len(advertiser_data["name"])) % 100),
            }
            response = client.post("/ml-scores", json=ml_score_payload)
            assert response.status_code == 200


def test_get_ad():
    for client_data in test_clients_data:
        client_id = client_data["client_id"]

        response = client.get(f"/ads?client_id={client_id}")
        if response.status_code == 200:
            ad = response.json()
            targeting = client.get(
                f"/advertisers/{ad['advertiser_id']}/campaigns/{ad['ad_id']}"
            ).json()["targeting"]
            assert (
                targeting["gender"] == "ALL"
                or targeting["gender"] == client_data["gender"]
            )
            assert client_data["age"] >= targeting["age_from"]
            assert client_data["age"] <= targeting["age_to"]
            assert client_data["location"] == targeting["location"]

            response = client.get(f"/ads?client_id={client_id}")
            if response.status_code == 200:
                next_ad = response.json()
                assert next_ad["ad_id"] != ad["ad_id"]
            else:
                assert response.status_code == 404
        else:
            assert response.status_code == 404

    for client_data in test_clients_data:
        client_id = client_data["client_id"]

        updated_client_data = copy(client_data)
        updated_client_data["location"] = "non_matching_location"
        response = client.post("/clients/bulk", json=[updated_client_data])
        assert response.status_code == 201

        response = client.get(f"/ads?client_id={client_id}")
        assert response.status_code == 404


def test_advance_time():
    response = client.post("/time/advance", json={"current_date": 0})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["current_date"] == 0

    response = client.post("/time/advance", json={"current_date": 5})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["current_date"] == 5

    response = client.post("/time/advance", json={"current_date": 6})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["current_date"] == 6
