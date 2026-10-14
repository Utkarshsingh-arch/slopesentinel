"""Pure Python Risk Engine for SlopeSentinel.

Computes a deterministic, transparent, and reproducible experimental risk index (0-100)
from normalized multi-criteria components:
- Susceptibility (baseline geological vulnerability)
- Rainfall trigger (effective precipitation from weather or scenario override)
- Soil moisture anomaly (VWC % relative to saturation thresholds)
- Tilt anomaly (angular ground displacement relative to critical shear threshold)

DISCLAIMER:
The resulting score is an experimental demonstrator index for scenario exploration.
It is NOT a scientifically calibrated landslide probability or official warning.
"""

from typing import List, Tuple
from ..config import settings
from ..models.schemas import RiskComponents, SensorReading, WeatherData


def calculate_rainfall_score(
    weather: WeatherData,
    scenario_override_precip_mm: float | None = None,
) -> Tuple[float, float]:
    """Computes effective precipitation and normalized rainfall trigger score (0-100)."""
    # Use the higher of current rain, 24h forecast, or scenario override
    base_precip = max(weather.current_precipitation_mm, weather.forecast_24h_precip_mm)
    if scenario_override_precip_mm is not None:
        effective_precip = max(base_precip, scenario_override_precip_mm)
    else:
        effective_precip = base_precip

    max_thresh = settings.thresholds.rainfall_max_trigger_mm
    score = min(100.0, max(0.0, (effective_precip / max_thresh) * 100.0))
    return round(score, 1), round(effective_precip, 1)


def calculate_soil_moisture_score(vwc_pct: float) -> float:
    """Normalizes soil volumetric water content (VWC %) into a 0-100 anomaly score."""
    min_vwc = settings.thresholds.soil_moisture_min_vwc
    max_vwc = settings.thresholds.soil_moisture_max_vwc

    if vwc_pct <= min_vwc:
        return 0.0
    if vwc_pct >= max_vwc:
        return 100.0

    score = ((vwc_pct - min_vwc) / (max_vwc - min_vwc)) * 100.0
    return round(min(100.0, max(0.0, score)), 1)


def calculate_tilt_score(tilt_degrees: float) -> float:
    """Normalizes biaxial angular displacement (degrees) into a 0-100 anomaly score."""
    max_deg = settings.thresholds.tilt_max_deg
    score = (tilt_degrees / max_deg) * 100.0
    return round(min(100.0, max(0.0, score)), 1)


def compute_risk_evaluation(
    baseline_susceptibility: float,
    sensor: SensorReading,
    weather: WeatherData,
    scenario_override_precip_mm: float | None = None,
) -> Tuple[RiskComponents, float, List[str]]:
    """Evaluates geotechnical slope risk and identifies key contributing factors.

    Returns:
        RiskComponents: Individual normalized scores (0-100)
        risk_index: Weighted composite index (0-100)
        contributing_factors: List of human-readable dominant triggers
    """
    susc_score = round(min(100.0, max(0.0, baseline_susceptibility)), 1)
    rain_score, effective_precip = calculate_rainfall_score(weather, scenario_override_precip_mm)
    soil_score = calculate_soil_moisture_score(sensor.soil_moisture_vwc)
    tilt_score = calculate_tilt_score(sensor.tilt_degrees)

    w = settings.risk_weights
    composite = (
        (w.weight_susceptibility * susc_score)
        + (w.weight_rainfall * rain_score)
        + (w.weight_soil_moisture * soil_score)
        + (w.weight_tilt * tilt_score)
    )
    risk_index = round(min(100.0, max(0.0, composite)), 1)

    components = RiskComponents(
        susceptibility_score=susc_score,
        rainfall_score=rain_score,
        soil_moisture_score=soil_score,
        tilt_score=tilt_score,
    )

    # Rank factors by raw component severity score (0-100) to surface primary anomalies
    ranked_factors = [
        (
            tilt_score,
            f"Ground tilt anomaly ({sensor.tilt_degrees}° displacement, score {tilt_score}/100)",
        ),
        (
            rain_score,
            f"Precipitation trigger ({effective_precip}mm effective rain, score {rain_score}/100)",
        ),
        (
            soil_score,
            f"Soil water saturation ({sensor.soil_moisture_vwc}% VWC, score {soil_score}/100)",
        ),
        (
            susc_score,
            f"Baseline terrain susceptibility ({susc_score}/100)",
        ),
    ]

    # Sort descending by normalized severity
    ranked_factors.sort(key=lambda x: x[0], reverse=True)
    top_factors = [item[1] for item in ranked_factors[:2]]

    return components, risk_index, top_factors
