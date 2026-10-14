"""FastAPI Application for SlopeSentinel.

Provides dashboard API endpoints combining:
1. Live/cached weather via Open-Meteo
2. Deterministic simulated ground sensor telemetry
3. Pure Python multi-criteria risk engine
4. Exposure-grounded response priority engine
5. Illustrative geospatial polygons and asset overlays for Gangtok
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Literal
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models.schemas import (
    HealthResponse,
    DashboardPayload,
    SiteMeta,
    DataProvenance,
    IllustrativeAsset,
)
from .services import weather_provider, sensor_provider, priority_engine

# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Regional Landslide Intelligence & Emergency Response Platform (Gangtok Demo)",
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load static demo zones and assets
DEMO_DATA_PATH = Path(__file__).resolve().parent / "data" / "demo_zones.json"


def load_demo_dataset():
    if not DEMO_DATA_PATH.exists():
        raise RuntimeError(f"Demo dataset missing at {DEMO_DATA_PATH}")
    with open(DEMO_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health probe verifying service availability and execution mode."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.environment,
        is_official_warning=False,
    )


@app.get("/api/dashboard", response_model=DashboardPayload)
async def get_dashboard(
    scenario: Literal["baseline", "heavy_rain", "tilt_anomaly"] = Query(
        default="baseline",
        description="Selectable operational scenario (baseline, heavy_rain, tilt_anomaly)",
    ),
    refresh: bool = Query(
        default=False,
        description="Force bypass of weather TTL cache for fresh Open-Meteo query",
    ),
):
    """Consolidated dashboard state endpoint for presentation and map overlays."""
    try:
        raw_dataset = load_demo_dataset()
        zones_data = raw_dataset.get("zones", [])
        raw_assets = raw_dataset.get("illustrative_assets", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load demo geographic dataset: {str(e)}")

    # 1. Fetch weather (Live, cached, or fallback)
    weather_data = await weather_provider.get_weather(force_refresh=refresh)

    # 2. Ingest deterministic simulated sensor telemetry for requested scenario
    scenario_info, sensor_readings = sensor_provider.get_telemetry_for_scenario(scenario)

    # 3. Evaluate and rank zones via Risk & Priority engines
    evaluated_zones = priority_engine.evaluate_and_rank_zones(
        zones_data=zones_data,
        sensor_readings=sensor_readings,
        weather=weather_data,
        scenario_override_precip_mm=scenario_info.simulated_rainfall_override_mm,
    )

    # Parse illustrative assets
    illustrative_assets = [IllustrativeAsset(**asset) for asset in raw_assets]

    # Assemble site metadata
    now_iso = datetime.now(timezone.utc).isoformat()
    meta = SiteMeta(
        site_id=settings.site.site_id,
        site_name=settings.site.site_name,
        region=settings.site.region,
        latitude=settings.site.latitude,
        longitude=settings.site.longitude,
        elevation_m=settings.site.elevation_m,
        evaluated_at=now_iso,
        disclaimer=settings.disclaimer,
        is_official_warning=False,
    )

    # Assembly provenance metadata
    provenance = DataProvenance(
        weather_source=weather_data.source,
        weather_status=weather_data.source_status,
        sensor_mode="SIMULATED",
        zones_mode="ILLUSTRATIVE_DEMO_DATA",
        algorithm_notice="DETERMINISTIC_HEURISTIC_DEMO",
    )

    return DashboardPayload(
        meta=meta,
        scenario=scenario_info,
        weather=weather_data,
        sensors=list(sensor_readings.values()),
        zones=evaluated_zones,
        illustrative_assets=illustrative_assets,
        data_provenance=provenance,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
