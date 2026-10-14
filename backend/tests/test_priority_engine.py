"""Tests for PriorityEngine and zone ranking logic."""

import pytest
from backend.services.priority_engine import PriorityEngine, determine_status_level
from backend.models.schemas import WeatherData, SensorReading


@pytest.fixture
def dummy_weather() -> WeatherData:
    return WeatherData(
        source="Test Provider",
        source_status="live",
        timestamp="2026-10-15T00:00:00Z",
        temperature_c=18.0,
        relative_humidity_pct=75.0,
        apparent_temperature_c=18.0,
        current_precipitation_mm=0.0,
        forecast_24h_precip_mm=5.0,
        wind_speed_kmh=5.0,
        weather_code=1,
        condition_text="Clear",
        is_fallback=False,
    )


@pytest.fixture
def mock_zones_data():
    return [
        {
            "zone_id": "zone_low_risk",
            "zone_name": "Low Risk Demo Zone",
            "description": "Low slope demo zone",
            "centroid": [27.35, 88.61],
            "sensor_node_id": "NODE-01",
            "baseline_susceptibility": 30.0,
            "exposure_score": 30.0,
            "exposed_assets": ["Local Trail"],
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[88.61, 27.35], [88.62, 27.35], [88.62, 27.36], [88.61, 27.36], [88.61, 27.35]]],
            },
        },
        {
            "zone_id": "zone_high_risk",
            "zone_name": "High Risk Demo Zone",
            "description": "High slope demo zone",
            "centroid": [27.32, 88.59],
            "sensor_node_id": "NODE-02",
            "baseline_susceptibility": 80.0,
            "exposure_score": 90.0,
            "exposed_assets": ["State Highway NH-10"],
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[88.58, 27.31], [88.60, 27.31], [88.60, 27.32], [88.58, 27.32], [88.58, 27.31]]],
            },
        },
    ]


def test_status_level_tiers():
    assert determine_status_level(85.0) == "Critical"
    assert determine_status_level(75.0) == "Critical"
    assert determine_status_level(65.0) == "Elevated"
    assert determine_status_level(55.0) == "Elevated"
    assert determine_status_level(45.0) == "Watch"
    assert determine_status_level(30.0) == "Watch"
    assert determine_status_level(20.0) == "Low"


def test_priority_ranking_sort_order(mock_zones_data, dummy_weather):
    sensors = {
        "zone_low_risk": SensorReading(
            node_id="NODE-01",
            zone_id="zone_low_risk",
            timestamp="2026-10-15T00:00:00Z",
            is_simulated=True,
            data_source="SIMULATED",
            soil_moisture_vwc=22.0,
            soil_moisture_status="Normal",
            tilt_degrees=0.1,
            tilt_status="Stable",
            battery_pct=95,
            signal_rssi_dbm=-75,
            operational_status="ONLINE",
        ),
        "zone_high_risk": SensorReading(
            node_id="NODE-02",
            zone_id="zone_high_risk",
            timestamp="2026-10-15T00:00:00Z",
            is_simulated=True,
            data_source="SIMULATED",
            soil_moisture_vwc=82.0,
            soil_moisture_status="Saturated",
            tilt_degrees=4.0,
            tilt_status="Active Creep",
            battery_pct=88,
            signal_rssi_dbm=-82,
            operational_status="ONLINE",
        ),
    }

    evaluated = PriorityEngine.evaluate_and_rank_zones(
        zones_data=mock_zones_data,
        sensor_readings=sensors,
        weather=dummy_weather,
        scenario_override_precip_mm=None,
    )

    assert len(evaluated) == 2
    # The high risk zone must be ranked #1
    assert evaluated[0].zone_id == "zone_high_risk"
    assert evaluated[0].priority_rank == 1
    assert evaluated[0].priority_score > evaluated[1].priority_score
    assert evaluated[1].zone_id == "zone_low_risk"
    assert evaluated[1].priority_rank == 2
