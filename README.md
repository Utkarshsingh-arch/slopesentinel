# SlopeSentinel: AI-Assisted Landslide Intelligence & Emergency-Response Platform

> **DEMONSTRATION & PROTOTYPE NOTICE:**  
> **NOT AN OFFICIAL WARNING SYSTEM OR DISASTER FORECAST.**  
> SlopeSentinel is an exploratory decision-support demonstration tool designed for regional landslide risk awareness in the Gangtok region (Sikkim, India). The zones, hazard boundaries, infrastructure exposure values, and sensor readings generated in this prototype are **illustrative and simulated demo data**. They do NOT represent official Geological Survey of India (GSI) hazard maps, real-time verified sensor deployments, or certified meteorological warnings.

---

## 1. Project Vision

SlopeSentinel is designed to provide localized, AI-assisted landslide intelligence and emergency-response prioritization for mountainous terrain, focused initially on the pilot area surrounding **Gangtok, Sikkim, India** (Latitude: `27.3389° N`, Longitude: `88.6065° E`).

The long-term platform vision integrates:
- **Atmospheric Context:** Real-time meteorological data and short-term precipitation forecasts.
- **Physical Ground Telemetry:** Low-power IoT soil moisture and biaxial tilt sensors.
- **Resilient Mesh Communications:** LoRa and ad-hoc wireless relay topologies for rugged highland environments.
- **Transparent Risk Modeling:** Explainable heuristics combining slope susceptibility, cumulative moisture saturation, and kinematic tilt anomalies.
- **Infrastructure Impact Prioritization:** GIS-grounded exposure mapping for arterial corridors and settlement clusters.
- **Incident Coordination:** Field dispatch coordination and emergency service resource allocation.

---

## 2. Immediate Demonstration Scope (MVP)

The initial working demo provides an end-to-end local capability:
1. **Live Weather Integration:** Retrieves real-time weather and forecast precipitation for Gangtok via the Open-Meteo API, with robust caching, timestamps, and automatic offline fallback.
2. **Deterministic Sensor Simulation:** Generates clearly labelled simulated sensor readings (`SIMULATED`) for soil volumetric water content and angular slope tilt across multiple operational scenarios.
3. **Transparent Risk Engine:** A pure Python deterministic heuristic calculating component scores and an experimental 0–100 risk index.
4. **Response Priority Engine:** Combines the experimental risk index with illustrative asset exposure to rank response zones.
5. **Interactive Geospatial Visualization:** Leaflet-based map centered on Gangtok showing illustrative zone geometries color-coded by response urgency, with OpenStreetMap attribution.
6. **Scenario Switching:** Instant switching between **Baseline**, **Heavy Rainfall + Wet Soil**, and **Abnormal Tilt** scenarios without server restarts.

---

## 3. Data Integrity & Provenance Contract

To maintain absolute transparency during demonstrations:
- **Live Weather:** Retrieved from Open-Meteo with explicit timestamp and provenance.
- **Simulated Sensors:** Plainly designated with `SIMULATED` tags. No physical hardware is claimed.
- **Illustrative Zones:** Defined as demo scenario regions with explicit disclaimers.
- **Heuristic Indices:** Computed as demonstration risk and response-priority scores, not official landslide probabilities.

---

## 4. Architecture Overview

```
                                [ Open-Meteo API ]
                                         │ (Live forecast / Precipitation)
                                         ▼
   [ Scenario Selector ] ──► [ WeatherProvider ] (Caching & Fallback)
            │                            │
            ▼                            ▼
  [ DemoSensorProvider ] ────► [ RiskEngine (Pure Python) ]
 (Soil Moisture / Tilt)                  │
                                         ▼
  [ Illustrative GeoJSON ] ──► [ PriorityEngine ]
  (Zones & Exposure)                     │
                                         ▼
                                 [ FastAPI Backend ]
                                         │ JSON Payload
                                         ▼
                             [ React + Vite + Leaflet ]
                             (Interactive Map & Ranking)
```

For complete technical specifications, see [ARCHITECTURE.md](file:///C:/Users/gagan/NexuxEdu/slopesentinel/ARCHITECTURE.md).
