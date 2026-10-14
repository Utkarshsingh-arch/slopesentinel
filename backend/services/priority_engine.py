"""Priority Engine for SlopeSentinel.

Harmonizes geotechnical experimental risk with socio-economic and infrastructure exposure
to compute a response-priority score (0-100) and an actionable ranked list.

DISCLAIMER:
The response-priority score is a demonstrator decision-support heuristic for emergency
dispatch prioritization. It does NOT represent a calibrated disaster-risk probability.
"""

from typing import List, Dict, Any, Literal
from ..config import settings
from ..models.schemas import (
    ZoneEvaluation,
    SensorReading,
    WeatherData,
    GeoPolygon,
)
from .risk_engine import compute_risk_evaluation


def determine_status_level(priority_score: float) -> Literal["Low", "Watch", "Elevated", "Critical"]:
    """Categorizes priority score into operational tiers."""
    if priority_score >= 75.0:
        return "Critical"
    if priority_score >= 55.0:
        return "Elevated"
    if priority_score >= 30.0:
        return "Watch"
    return "Low"


def generate_response_recommendation(
    level: str,
    zone_name: str,
    top_factor: str,
    exposed_assets: List[str],
) -> str:
    """Generates concise, role-appropriate emergency response advisory text."""
    primary_asset = exposed_assets[0] if exposed_assets else "critical infrastructure"
    if level == "Critical":
        return (
            f"URGENT DISPATCH: Pre-position rapid clearance crews along {primary_asset}. "
            f"Activate emergency detour protocols due to {top_factor}."
        )
    if level == "Elevated":
        return (
            f"ADVISORY: Issue transit cautionary notice for {primary_asset}. "
            f"Increase monitoring frequency and inspect drainage culverts."
        )
    if level == "Watch":
        return (
            f"WATCH: Maintain heightened sensor telemetry surveillance for {zone_name}. "
            f"Verify line-of-sight visual status."
        )
    return f"ROUTINE: Normal sensor heartbeat verification. No active response mobilization required for {zone_name}."


class PriorityEngine:
    """Evaluates and ranks geographic demo zones by response urgency."""

    @staticmethod
    def evaluate_and_rank_zones(
        zones_data: List[Dict[str, Any]],
        sensor_readings: Dict[str, SensorReading],
        weather: WeatherData,
        scenario_override_precip_mm: float | None = None,
    ) -> List[ZoneEvaluation]:
        evaluated_zones: List[ZoneEvaluation] = []

        w_risk = settings.priority_weights.risk_weight
        w_exp = settings.priority_weights.exposure_weight

        for z in zones_data:
            zone_id = z["zone_id"]
            sensor = sensor_readings.get(
                zone_id,
                # Fallback safe mock sensor if missing
                SensorReading(
                    node_id=z.get("sensor_node_id", f"NODE-{zone_id}"),
                    zone_id=zone_id,
                    timestamp=weather.timestamp,
                    is_simulated=True,
                    data_source="SIMULATED",
                    soil_moisture_vwc=30.0,
                    soil_moisture_status="Normal",
                    tilt_degrees=0.2,
                    tilt_status="Stable",
                    battery_pct=90,
                    signal_rssi_dbm=-80,
                    operational_status="ONLINE",
                ),
            )

            components, risk_index, top_factors = compute_risk_evaluation(
                baseline_susceptibility=float(z["baseline_susceptibility"]),
                sensor=sensor,
                weather=weather,
                scenario_override_precip_mm=scenario_override_precip_mm,
            )

            exposure_score = float(z["exposure_score"])
            raw_priority = (w_risk * risk_index) + (w_exp * exposure_score)
            priority_score = round(min(100.0, max(0.0, raw_priority)), 1)
            level = determine_status_level(priority_score)

            recommendation = generate_response_recommendation(
                level=level,
                zone_name=z["zone_name"],
                top_factor=top_factors[0] if top_factors else "Environmental triggers",
                exposed_assets=z.get("exposed_assets", []),
            )

            evaluated_zones.append(
                ZoneEvaluation(
                    zone_id=zone_id,
                    zone_name=z["zone_name"],
                    description=z["description"],
                    centroid=z["centroid"],
                    geometry=GeoPolygon(**z["geometry"]),
                    baseline_susceptibility=float(z["baseline_susceptibility"]),
                    exposure_score=exposure_score,
                    exposed_assets=z.get("exposed_assets", []),
                    sensor_telemetry=sensor,
                    risk_components=components,
                    risk_index=risk_index,
                    priority_score=priority_score,
                    priority_rank=1,  # Populated after sorting
                    status_level=level,
                    contributing_factors=top_factors,
                    response_recommendation=recommendation,
                    provenance_notice="ILLUSTRATIVE_DEMO_DATA",
                )
            )

        # Sort descending by priority score
        evaluated_zones.sort(key=lambda item: item.priority_score, reverse=True)

        # Assign ranks 1, 2, 3...
        for rank, item in enumerate(evaluated_zones, start=1):
            item.priority_rank = rank

        return evaluated_zones


priority_engine = PriorityEngine()
