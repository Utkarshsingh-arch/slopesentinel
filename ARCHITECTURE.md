# SlopeSentinel System Architecture

## 1. Architectural Philosophy

SlopeSentinel is structured around deterministic state separation, zero-trust data provenance, and modular service encapsulation. The core calculations are decoupled from external APIs and simulated hardware, allowing physical LoRa telemetry or advanced machine-learning models to be swapped in seamlessly in future iterations.

---

## 2. Component Taxonomy & Responsibilities

### A. WeatherProvider (`backend/services/weather.py`)
- **Responsibility:** Ingests atmospheric metrics from the public Open-Meteo REST API for Gangtok coordinates (`27.3389° N, 88.6065° E`).
- **Resilience:** Implements a strict HTTP timeout (5.0s), an in-memory TTL cache (15 minutes), and deterministic fallback payloads for offline/degraded operations.
- **Contract:** Every response explicitly includes `source_status` (`"live"`, `"cached"`, or `"fallback"`), retrieval timestamp, and forecast precipitation. Never falsely labels fallback or cached values as live observations.

### B. SensorProvider (`backend/services/sensor_simulator.py`)
- **Responsibility:** Generates reproducible, scenario-governed ground sensor telemetry for registered slope zones.
- **Telemetry Points:**
  - Soil Moisture: Volumetric Water Content (VWC %: 0.0 - 100.0%).
  - Slope Tilt: Biaxial displacement magnitude in degrees (°).
  - Node Status: Heartbeat and battery health metrics.
- **Designation:** Clearly labelled `data_source = "SIMULATED"`. Future hardware can implement the same `BaseSensorProvider` interface via MQTT or serial LoRa gateway listeners.

### C. RiskEngine (`backend/services/risk_engine.py`)
- **Responsibility:** A pure Python deterministic calculation module that evaluates slope stability risk.
- **Properties:**
  - Zero external I/O or network dependencies.
  - Normalized component scoring (0–100 scale).
  - Weighted factor aggregation with transparent formula documentation.
  - Generates human-readable factor contribution summaries.
  - Threshold classifications: `Low`, `Watch`, `Elevated`, `Critical`.

### D. PriorityEngine (`backend/services/priority_engine.py`)
- **Responsibility:** Combines geotechnical/environmental risk with socio-economic and infrastructural exposure.
- **Output:** Ranks geographic demo zones by `response_priority_score` (0–100) to assist emergency coordinators in prioritizing resource dispatch.

### E. Geographic Data Store (`backend/data/demo_zones.json`)
- **Responsibility:** Lightweight GeoJSON-compliant storage containing illustrative demo polygons for 3 Gangtok slope zones (e.g., East Ridge Corridor, Ranipool Catchment, Tathangchen Slope) and illustrative infrastructure assets.
- **Disclaimer:** Explicitly marked as illustrative demonstration boundaries.

### F. REST API (`backend/main.py`)
- **Framework:** FastAPI with Pydantic v2 schemas.
- **Endpoints:**
  - `GET /api/health`: Health probe and service uptime.
  - `GET /api/dashboard?scenario={scenario_id}&refresh={bool}`: Consolidated dashboard state payload.

### G. Geospatial Frontend (`frontend/`)
- **Stack:** React 18, Vite, TypeScript, Tailwind CSS, Leaflet, React-Leaflet.
- **Theme:** High-contrast tactical command dark theme (charcoal `#0B1120`, navy `#0F172A`, cyan `#06B6D4`, amber `#F59E0B`, red `#EF4444`).
- **Interactivity:** Reactive scenario switcher, interactive polygon maps, linked priority list focus, and dynamic data provenance indicators.

---

## 3. Mathematical Risk & Priority Formulation

The demonstrator utilizes a deterministic multi-criteria index:

### 3.1 Normalized Component Inputs ($0 - 100$)

1. **Susceptibility Score ($S_{\text{susc}}$):**  
   Baseline terrain vulnerability based on illustrative slope steepness and lithology ($0 - 100$).
2. **Rainfall Trigger Score ($R_{\text{rain}}$):**  
   Computed from observed and forecast precipitation (mm). Normalized against a demo trigger threshold ($50\text{ mm} \rightarrow 100$):
   $$R_{\text{rain}} = \min\left(100, \frac{\text{Rainfall}_{\text{eff}}}{50} \times 100\right)$$
   Where $\text{Rainfall}_{\text{eff}} = \text{max}(\text{weather\_precip}, \text{scenario\_override\_precip})$.
3. **Soil Moisture Anomaly Score ($M_{\text{soil}}$):**  
   Derived from volumetric water content (VWC %):
   $$M_{\text{soil}} = \min\left(100, \max\left(0, \frac{\text{VWC} - 20}{60} \times 100\right)\right)$$
4. **Tilt Anomaly Score ($T_{\text{tilt}}$):**  
   Derived from angular ground displacement ($\theta$ in degrees):
   $$T_{\text{tilt}} = \min\left(100, \frac{\theta}{5.0^\circ} \times 100\right)$$

### 3.2 Experimental Risk Index ($R_{\text{index}}$)

Weighted sum of normalized triggers:
$$R_{\text{index}} = w_{\text{susc}} S_{\text{susc}} + w_{\text{rain}} R_{\text{rain}} + w_{\text{soil}} M_{\text{soil}} + w_{\text{tilt}} T_{\text{tilt}}$$
*Demonstration Weights:*
$$w_{\text{susc}} = 0.20, \quad w_{\text{rain}} = 0.35, \quad w_{\text{soil}} = 0.25, \quad w_{\text{tilt}} = 0.20$$

### 3.3 Response Priority Score ($P_{\text{priority}}$)

Harmonizes geotechnical risk with illustrative exposure $E_{\text{expo}}$ (e.g., road corridors, population density):
$$P_{\text{priority}} = \min\left(100, 0.65 \times R_{\text{index}} + 0.35 \times E_{\text{expo}}\right)$$

### 3.4 Classification Tiers
- **$0 \le P < 30$:** Low (Routine monitoring)
- **$30 \le P < 55$:** Watch (Heightened awareness)
- **$55 \le P < 75$:** Elevated (Advisory & staging)
- **$75 \le P \le 100$:** Critical (Immediate response mobilization)

---

## 4. Extensibility Contract

```
                     ┌─────────────────────────┐
                     │   BaseSensorProvider    │
                     └────────────▲────────────┘
                                  │
          ┌───────────────────────┴───────────────────────┐
          │                                               │
┌─────────────────────────┐                   ┌─────────────────────────┐
│   DemoSensorProvider    │                   │   LoRaMqttSensorProvider│
│  (Deterministic Sim)    │                   │   (Physical Hardware)   │
└─────────────────────────┘                   └─────────────────────────┘
```

The `BaseSensorProvider` abstract contract enables seamless evolution from offline simulation to live LoRa mesh networks and physical sensor gateways without modifying downstream `RiskEngine` or `PriorityEngine` implementations.
