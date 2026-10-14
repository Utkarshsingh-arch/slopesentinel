"""Tests for pure Python RiskEngine calculations."""

import pytest
from backend.services.risk_engine import (
    calculate_rainfall_score,
    calculate_soil_moisture_score,
    calculate_tilt_score,
    compute_risk_evaluation,
)
from backend.models.schemas import WeatherData, SensorReading
from backend.config import settings


@pytest.fixture
def dummy_weather() -> WeatherData:
    return WeatherData(
        source="Test Weather",
        source_status="live",
        timestamp="2026-10-15T00:00:00Z",
        temperature_c=18.0,
        relative_humidity_pct=75.0,
        apparent_temperature_c=18.0,
        current_precipitation_mm=0.0,
        forecast_24h_precip_mm=10.0,
        wind_speed_kmh=5.0,
        weather_code=1,
        condition_text="Clear",
        is_fallback=False,
    )


@pytest.fixture
def dummy_sensor() -> SensorReading:
    return SensorReading(
        node_id="NODE-TEST-01",
        zone_id="zone_test",
        timestamp="2026-10-15T00:00:00Z",
        is_simulated=True,
        data_source="SIMULATED",
        soil_moisture_vwc=30.0,
        soil_moisture_status="Normal",
        tilt_degrees=0.2,
        tilt_status="Stable",
        battery_pct=95,
        signal_rssi_dbm=-75,
        operational_status="ONLINE",
    )


def test_rainfall_score_normalization(dummy_weather):
    # 10mm out of 50mm max threshold -> 20.0 score
    score, effective_precip = calculate_rainfall_score(dummy_weather)
    assert score == 20.0
    assert effective_precip == 10.0

    # With scenario override of 60mm -> clamped to 100.0 score
    score_override, effective_override = calculate_rainfall_score(dummy_weather, scenario_override_precip_mm=60.0)
    assert score_override == 100.0
    assert effective_override == 60.0

    # Zero rainfall -> 0.0 score
    zero_weather = dummy_weather.model_copy(update={"forecast_24h_precip_mm": 0.0, "current_precipitation_mm": 0.0})
    score_zero, _ = calculate_rainfall_score(zero_weather)
    assert score_zero == 0.0


def test_soil_moisture_score_normalization():
    # Below min (20%) -> 0.0
    assert calculate_soil_moisture_score(15.0) == 0.0
    assert calculate_soil_moisture_score(20.0) == 0.0

    # Above max (80%) -> 100.0
    assert calculate_soil_moisture_score(85.0) == 100.0
    assert calculate_soil_moisture_score(80.0) == 100.0

    # Midpoint: (50 - 20) / (80 - 20) = 30 / 60 = 50.0
    assert calculate_soil_moisture_score(50.0) == 50.0


def test_tilt_score_normalization():
    # 0.0 deg -> 0.0
    assert calculate_tilt_score(0.0) == 0.0

    # 2.5 deg out of 5.0 -> 50.0
    assert calculate_tilt_score(2.5) == 50.0

    # >= 5.0 deg -> 100.0 clamped
    assert calculate_tilt_score(5.0) == 100.0
    assert calculate_tilt_score(7.2) == 100.0


def test_compute_risk_evaluation_composite(dummy_weather, dummy_sensor):
    baseline_susc = 60.0
    components, risk_index, top_factors = compute_risk_evaluation(
        baseline_susceptibility=baseline_susc,
        sensor=dummy_sensor,
        weather=dummy_weather,
        scenario_override_precip_mm=None,
    )

    # Validate range
    assert 0.0 <= risk_index <= 100.0
    assert components.susceptibility_score == 60.0
    assert components.rainfall_score == 20.0  # 10mm / 50mm * 100
    assert components.soil_moisture_score == calculate_soil_moisture_score(30.0)
    assert components.tilt_score == calculate_tilt_score(0.2)

    # Validate mathematical weight application
    w = settings.risk_weights
    expected_composite = (
        (w.weight_susceptibility * components.susceptibility_score)
        + (w.weight_rainfall * components.rainfall_score)
        + (w.weight_soil_moisture * components.soil_moisture_score)
        + (w.weight_tilt * components.tilt_score)
    )
    assert risk_index == round(expected_composite, 1)

    # Check that top contributing factors are returned
    assert len(top_factors) == 2
    assert all(isinstance(f, str) and len(f) > 0 for f in top_factors)


def test_monotonic_risk_increase_with_triggers(dummy_weather, dummy_sensor):
    base_components, base_risk, _ = compute_risk_evaluation(
        baseline_susceptibility=50.0,
        sensor=dummy_sensor,
        weather=dummy_weather,
    )

    # Anomaly sensor with high tilt and wet soil
    severe_sensor = dummy_sensor.model_copy(update={"soil_moisture_vwc": 82.0, "tilt_degrees": 4.5})
    severe_components, severe_risk, _ = compute_risk_evaluation(
        baseline_susceptibility=50.0,
        sensor=severe_sensor,
        weather=dummy_weather,
        scenario_override_precip_mm=55.0,
    )

    assert severe_risk > base_risk
    assert severe_components.rainfall_score > base_components.rainfall_score
    assert severe_components.soil_moisture_score > base_components.soil_moisture_score
    assert severe_components.tilt_score > base_components.tilt_score
