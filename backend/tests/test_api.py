"""Integration tests for FastAPI dashboard and health endpoints."""

import pytest
from starlette.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "SlopeSentinel"
    assert data["environment"] == "demonstration"
    assert data["is_official_warning"] is False
    assert "timestamp" in data


def test_dashboard_baseline_scenario(client):
    response = client.get("/api/dashboard?scenario=baseline")
    assert response.status_code == 200
    data = response.json()

    # Meta
    assert data["meta"]["site_id"] == "GKT-REGIONAL-01"
    assert data["meta"]["latitude"] == 27.3389
    assert data["meta"]["longitude"] == 88.6065
    assert data["meta"]["is_official_warning"] is False

    # Scenario
    assert data["scenario"]["scenario_id"] == "baseline"
    assert data["scenario"]["is_hypothetical_override"] is False

    # Weather
    assert "temperature_c" in data["weather"]
    assert data["weather"]["source_status"] in ["live", "cached", "fallback"]

    # Zones
    assert len(data["zones"]) == 3
    # Check that rank 1 has the highest priority score
    scores = [z["priority_score"] for z in data["zones"]]
    assert scores == sorted(scores, reverse=True)
    assert data["zones"][0]["priority_rank"] == 1

    # Every sensor reading must be marked simulated
    for sensor in data["sensors"]:
        assert sensor["is_simulated"] is True
        assert sensor["data_source"] == "SIMULATED"

    # Illustrative assets
    assert len(data["illustrative_assets"]) >= 3


def test_dashboard_scenario_switching(client):
    # Test heavy rain
    res_rain = client.get("/api/dashboard?scenario=heavy_rain")
    assert res_rain.status_code == 200
    data_rain = res_rain.json()
    assert data_rain["scenario"]["scenario_id"] == "heavy_rain"
    assert data_rain["scenario"]["is_hypothetical_override"] is True
    assert data_rain["scenario"]["simulated_rainfall_override_mm"] == 68.5

    # Test tilt anomaly
    res_tilt = client.get("/api/dashboard?scenario=tilt_anomaly")
    assert res_tilt.status_code == 200
    data_tilt = res_tilt.json()
    assert data_tilt["scenario"]["scenario_id"] == "tilt_anomaly"
    assert data_tilt["scenario"]["is_hypothetical_override"] is True
    
    # In tilt anomaly, Ranipool flank must be #1 priority due to acute tilt (4.35 deg)
    assert data_tilt["zones"][0]["zone_id"] == "zone_ranipool_catchment"
    assert data_tilt["zones"][0]["status_level"] in ["Elevated", "Critical"]


def test_dashboard_invalid_scenario_returns_validation_error(client):
    response = client.get("/api/dashboard?scenario=invalid_xyz")
    assert response.status_code == 422
