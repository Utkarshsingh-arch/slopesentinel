"""Tests for deterministic DemoSensorProvider."""

from backend.services.sensor_simulator import DemoSensorProvider


def test_sensor_provider_scenarios_exist():
    provider = DemoSensorProvider()
    scenarios = provider.get_available_scenarios()
    assert "baseline" in scenarios
    assert "heavy_rain" in scenarios
    assert "tilt_anomaly" in scenarios


def test_sensor_provider_deterministic_readings():
    provider = DemoSensorProvider()
    
    # Run twice for baseline
    _, readings_1 = provider.get_telemetry_for_scenario("baseline")
    _, readings_2 = provider.get_telemetry_for_scenario("baseline")

    assert set(readings_1.keys()) == set(readings_2.keys())
    for zone_id in readings_1:
        r1 = readings_1[zone_id]
        r2 = readings_2[zone_id]
        assert r1.soil_moisture_vwc == r2.soil_moisture_vwc
        assert r1.tilt_degrees == r2.tilt_degrees
        assert r1.is_simulated is True
        assert r1.data_source == "SIMULATED"


def test_scenario_differences():
    provider = DemoSensorProvider()
    info_base, base_sensors = provider.get_telemetry_for_scenario("baseline")
    info_rain, rain_sensors = provider.get_telemetry_for_scenario("heavy_rain")
    info_tilt, tilt_sensors = provider.get_telemetry_for_scenario("tilt_anomaly")

    # Baseline has no override
    assert info_base.is_hypothetical_override is False
    assert info_base.simulated_rainfall_override_mm is None

    # Heavy rain has high rainfall override and higher moisture than baseline
    assert info_rain.is_hypothetical_override is True
    assert info_rain.simulated_rainfall_override_mm == 68.5
    assert rain_sensors["zone_east_ridge"].soil_moisture_vwc > base_sensors["zone_east_ridge"].soil_moisture_vwc
    assert rain_sensors["zone_ranipool_catchment"].soil_moisture_vwc > 80.0

    # Tilt anomaly has critical tilt on Ranipool
    assert info_tilt.is_hypothetical_override is True
    assert tilt_sensors["zone_ranipool_catchment"].tilt_degrees > 4.0
    assert "CRITICAL" in tilt_sensors["zone_ranipool_catchment"].tilt_status.upper()
