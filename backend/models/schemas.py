"""Pydantic schemas for SlopeSentinel API contracts."""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str = "SlopeSentinel"
    version: str = "1.0.0-mvp"
    timestamp: str
    environment: str = "demonstration"
    is_official_warning: bool = False


class WeatherData(BaseModel):
    source: str = Field("Open-Meteo API", description="Source organization or provider")
    source_status: Literal["live", "cached", "fallback"] = Field(
        ..., description="Data provenance: live query, TTL-cached query, or offline fallback"
    )
    timestamp: str = Field(..., description="Timestamp of observation or forecast retrieval")
    temperature_c: float
    relative_humidity_pct: float
    apparent_temperature_c: float
    current_precipitation_mm: float
    forecast_24h_precip_mm: float
    wind_speed_kmh: float
    weather_code: int
    condition_text: str
    is_fallback: bool = False
    notes: Optional[str] = None


class SensorReading(BaseModel):
    node_id: str
    zone_id: str
    timestamp: str
    is_simulated: bool = Field(True, description="Always True for demo simulator")
    data_source: str = Field("SIMULATED", description="Data provenance tag")
    soil_moisture_vwc: float = Field(..., description="Volumetric water content percentage (0-100%)")
    soil_moisture_status: str
    tilt_degrees: float = Field(..., description="Angular biaxial displacement magnitude in degrees")
    tilt_status: str
    battery_pct: int
    signal_rssi_dbm: int
    operational_status: Literal["ONLINE", "DEGRADED", "OFFLINE"] = "ONLINE"


class RiskComponents(BaseModel):
    susceptibility_score: float = Field(..., description="Baseline geological susceptibility (0-100)")
    rainfall_score: float = Field(..., description="Effective rainfall trigger score (0-100)")
    soil_moisture_score: float = Field(..., description="Soil moisture saturation anomaly (0-100)")
    tilt_score: float = Field(..., description="Kinematic tilt displacement score (0-100)")


class GeoPolygon(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[List[float]]] = Field(..., description="GeoJSON coordinates [lon, lat]")


class IllustrativeAsset(BaseModel):
    asset_id: str
    name: str
    category: Literal["road_corridor", "settlement", "critical_facility", "transit_hub"]
    description: str
    exposure_rating: int = Field(..., ge=0, le=100)
    coordinates: List[float] = Field(..., description="[lon, lat]")


class ZoneEvaluation(BaseModel):
    zone_id: str
    zone_name: str
    description: str
    centroid: List[float] = Field(..., description="[lat, lon]")
    geometry: GeoPolygon
    baseline_susceptibility: float
    exposure_score: float
    exposed_assets: List[str]
    sensor_telemetry: SensorReading
    risk_components: RiskComponents
    risk_index: float = Field(..., ge=0, le=100, description="Heuristic experimental risk index (0-100)")
    priority_score: float = Field(..., ge=0, le=100, description="Response priority score (0-100)")
    priority_rank: int = Field(..., ge=1)
    status_level: Literal["Low", "Watch", "Elevated", "Critical"]
    contributing_factors: List[str]
    response_recommendation: str
    provenance_notice: str = "ILLUSTRATIVE_DEMO_DATA"


class ScenarioInfo(BaseModel):
    scenario_id: str
    title: str
    description: str
    is_hypothetical_override: bool
    simulated_rainfall_override_mm: Optional[float] = None


class SiteMeta(BaseModel):
    site_id: str
    site_name: str
    region: str
    latitude: float
    longitude: float
    elevation_m: int
    evaluated_at: str
    disclaimer: str
    is_official_warning: bool = False


class DataProvenance(BaseModel):
    weather_source: str
    weather_status: Literal["live", "cached", "fallback"]
    sensor_mode: str = "SIMULATED"
    zones_mode: str = "ILLUSTRATIVE_DEMO_DATA"
    algorithm_notice: str = "DETERMINISTIC_HEURISTIC_DEMO"


class DashboardPayload(BaseModel):
    meta: SiteMeta
    scenario: ScenarioInfo
    weather: WeatherData
    sensors: List[SensorReading]
    zones: List[ZoneEvaluation]
    illustrative_assets: List[IllustrativeAsset]
    data_provenance: DataProvenance
