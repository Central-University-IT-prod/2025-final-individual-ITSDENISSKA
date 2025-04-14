import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.main import app
from datetime import datetime

client = TestClient(app)
random_location = str(uuid.uuid4())


@pytest.fixture
def sample_advertiser():
    return {
        "advertiser_id": str(uuid.uuid4()),
        "name": "Test Advertiser",
    }


@pytest.fixture
def sample_campaign(sample_advertiser):
    return {
        "impressions_limit": 200,
        "clicks_limit": 100,
        "cost_per_impression": 0.1,
        "cost_per_click": 0.5,
        "ad_title": "Test Campaign",
        "ad_text": "Sample text",
        "start_date": 1,
        "end_date": 7,
        "targeting": {
            "gender": "MALE",
            "age_from": 102,
            "age_to": 104,
            "location": random_location,
        },
    }


@pytest.fixture
def sample_client():
    return {
        "client_id": str(uuid.uuid4()),
        "login": "test_user",
        "age": 103,
        "location": random_location,
        "gender": "MALE",
    }


@pytest.fixture
def setup_data(sample_advertiser, sample_campaign, sample_client):
    response = client.post("/advertisers/bulk", json=[sample_advertiser])
    assert response.status_code == status.HTTP_201_CREATED
    advertiser_id = sample_advertiser["advertiser_id"]
    response = client.post(
        f"/advertisers/{advertiser_id}/campaigns", json=sample_campaign
    )
    assert response.status_code == status.HTTP_201_CREATED
    campaign_id = response.json()["campaign_id"]
    response = client.post("/clients/bulk", json=[sample_client])
    assert response.status_code == status.HTTP_201_CREATED
    response = client.post("/time/advance", json={"current_date": 1})
    assert response.status_code == status.HTTP_200_OK
    return {
        "advertiser_id": advertiser_id,
        "campaign_id": campaign_id,
        "client_id": sample_client["client_id"],
    }


def test_multi_day_stats(setup_data, client=client):
    advertiser_id = setup_data["advertiser_id"]
    campaign_id = setup_data["campaign_id"]

    # Create a list of clients
    clients = [
        {
            "client_id": str(uuid.uuid4()),
            "login": f"user_{i}",
            "age": 103,
            "location": random_location,
            "gender": "MALE",
        }
        for i in range(10)  # 10 unique clients
    ]

    # Add clients to the system
    response = client.post("/clients/bulk", json=clients)
    assert response.status_code == status.HTTP_201_CREATED

    # Day 1: Simulate impressions and clicks with unique clients
    for i, client_data in enumerate(clients[:5]):  # 5 unique clients on day 1
        client_id = client_data["client_id"]
        response = client.get(f"/ads?client_id={client_id}")
        assert response.status_code == status.HTTP_200_OK
        ad_response = response.json()
        if i < 5:  # All 5 clients make a click
            response = client.post(
                f"/ads/{ad_response['ad_id']}/click", json={"client_id": client_id}
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT

    # Advance to Day 2
    response = client.post("/time/advance", json={"current_date": 2})
    assert response.status_code == status.HTTP_200_OK

    # Day 2: Simulate more impressions and clicks with unique clients
    for i, client_data in enumerate(clients[5:8]):  # 3 unique clients on day 2
        client_id = client_data["client_id"]
        response = client.get(f"/ads?client_id={client_id}")
        assert response.status_code == status.HTTP_200_OK
        ad_response = response.json()
        if i < 2:  # 2 clients make a click
            response = client.post(
                f"/ads/{ad_response['ad_id']}/click", json={"client_id": client_id}
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT

    # Advance to Day 3
    response = client.post("/time/advance", json={"current_date": 3})
    assert response.status_code == status.HTTP_200_OK

    # Day 3: Simulate fewer impressions with unique clients
    for client_data in clients[8:10]:  # 2 unique clients on day 3
        client_id = client_data["client_id"]
        response = client.get(f"/ads?client_id={client_id}")
        assert response.status_code == status.HTTP_200_OK

    # Check daily stats for the campaign
    response = client.get(f"/stats/campaigns/{campaign_id}/daily")
    assert response.status_code == status.HTTP_200_OK
    daily_stats = response.json()

    # Verify Day 1 stats
    day_1_stats = next((day for day in daily_stats if day["date"] == 1), None)
    assert day_1_stats is not None
    assert day_1_stats["impressions_count"] == 5  # 5 unique impressions
    assert day_1_stats["clicks_count"] == 5  # 5 unique clicks
    assert day_1_stats["conversion"] == 100.0
    assert day_1_stats["spent_impressions"] == 0.5
    assert day_1_stats["spent_clicks"] == 2.5
    assert day_1_stats["spent_total"] == 3.0

    # Verify Day 2 stats
    day_2_stats = next((day for day in daily_stats if day["date"] == 2), None)
    assert day_2_stats is not None
    assert day_2_stats["impressions_count"] == 3  # 3 unique impressions
    assert day_2_stats["clicks_count"] == 2  # 2 unique clicks
    assert day_2_stats["conversion"] == (2 / 3) * 100
    assert round(day_2_stats["spent_impressions"], 1) == 0.3
    assert day_2_stats["spent_clicks"] == 1.0
    assert day_2_stats["spent_total"] == 1.3

    # Verify Day 3 stats
    day_3_stats = next((day for day in daily_stats if day["date"] == 3), None)
    assert day_3_stats is not None
    assert day_3_stats["impressions_count"] == 2  # 2 unique impressions
    assert day_3_stats["clicks_count"] == 0  # No clicks
    assert day_3_stats["conversion"] == 0.0
    assert day_3_stats["spent_impressions"] == 0.2
    assert day_3_stats["spent_clicks"] == 0.0
    assert day_3_stats["spent_total"] == 0.2

    # Check overall campaign stats
    response = client.get(f"/stats/campaigns/{campaign_id}")
    assert response.status_code == status.HTTP_200_OK
    campaign_stats = response.json()
    assert campaign_stats["impressions_count"] == 10  # Total unique impressions
    assert campaign_stats["clicks_count"] == 7  # Total unique clicks
    assert campaign_stats["conversion"] == (7 / 10) * 100
    assert round(campaign_stats["spent_impressions"], 1) == 1.0
    assert campaign_stats["spent_clicks"] == 3.5
    assert campaign_stats["spent_total"] == 4.5

    # Check advertiser stats
    response = client.get(f"/stats/advertisers/{advertiser_id}/campaigns")
    assert response.status_code == status.HTTP_200_OK
    advertiser_stats = response.json()
    assert advertiser_stats["impressions_count"] == 10
    assert advertiser_stats["clicks_count"] == 7
    assert advertiser_stats["conversion"] == (7 / 10) * 100
    assert round(advertiser_stats["spent_impressions"], 1) == 1.0
    assert advertiser_stats["spent_clicks"] == 3.5
    assert advertiser_stats["spent_total"] == 4.5

    # Check advertiser daily stats
    response = client.get(f"/stats/advertisers/{advertiser_id}/campaigns/daily")
    assert response.status_code == status.HTTP_200_OK
    advertiser_daily_stats = response.json()
    assert int(len(advertiser_daily_stats)) == 3
    assert advertiser_daily_stats[0] == day_1_stats
    assert advertiser_daily_stats[1] == day_2_stats
    assert advertiser_daily_stats[2] == day_3_stats
