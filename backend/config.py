"""SlopeSentinel Configuration Module.

All initial component weights, normalization bounds, and operational thresholds
are defined here as configurable parameters rather than hardcoded throughout the system.

DISCLAIMER: These are demonstrator calibration parameters for presentation purposes
and do not represent scientifically certified landslide threshold models.
"""

from pydantic import BaseModel, Field


class SiteConfig(BaseModel):
    site_id: str = "GKT-REGIONAL-01"
    site_name: str = "Gangtok & Surrounding Slopes"
    region: str = "East Sikkim, India"
    latitude: float = 27.3389
    longitude: float = 88.6065
    elevation_m: int = 1650


class WeatherConfig(BaseModel):
    open_meteo_url: str = "https://api.open-meteo.com/v1/forecast"
    request_timeout_seconds: float = 5.0
    cache_ttl_seconds: int = 900  # 15 minutes


class RiskEngineWeights(BaseModel):
    weight_susceptibility: float = Field(0.20, description="Baseline lithological/slope susceptibility weight")
    weight_rainfall: float = Field(0.35, description="Effective rainfall trigger weight")
    weight_soil_moisture: float = Field(0.25, description="Simulated soil saturation weight")
    weight_tilt: float = Field(0.20, description="Simulated ground tilt displacement weight")


class NormalizationThresholds(BaseModel):
    # Rainfall: 50mm cumulative trigger maps to 100/100 trigger score
    rainfall_max_trigger_mm: float = 50.0
    
    # Soil Moisture (Volumetric Water Content %):
    # Baseline ~20% = 0 anomaly score, >=80% = 100 anomaly score
    soil_moisture_min_vwc: float = 20.0
    soil_moisture_max_vwc: float = 80.0
    
    # Tilt: 0.0° = 0 score, >=5.0° = 100 score
    tilt_max_deg: float = 5.0


class PriorityWeights(BaseModel):
    # Combines geotechnical risk index (65%) with illustrative infrastructure exposure (35%)
    risk_weight: float = 0.65
    exposure_weight: float = 0.35


class Settings(BaseModel):
    app_name: str = "SlopeSentinel"
    app_version: str = "1.0.0-mvp"
    environment: str = "demonstration"
    
    site: SiteConfig = SiteConfig()
    weather: WeatherConfig = WeatherConfig()
    risk_weights: RiskEngineWeights = RiskEngineWeights()
    thresholds: NormalizationThresholds = NormalizationThresholds()
    priority_weights: PriorityWeights = PriorityWeights()
    
    disclaimer: str = (
        "DEMO PROTOTYPE ONLY: Values, sensor outputs, and zone boundaries are simulated "
        "or illustrative for demonstration purposes. This system is NOT an official "
        "early warning system and does NOT constitute certified GSI hazard advice."
    )


settings = Settings()
