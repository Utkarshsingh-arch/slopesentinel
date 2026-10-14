"""Deterministic Sensor Simulator for SlopeSentinel.

Generates reproducible, scenario-specific telemetry for ground slope monitoring nodes.
Telemetry includes Volumetric Water Content (VWC %) and Biaxial Tilt Displacement (°).

IMPORTANT: All outputs are explicitly stamped with data_source='SIMULATED' and
is_simulated=True. No physical IoT hardware is connected.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from datetime import datetime, timezone

from ..models.schemas import SensorReading, ScenarioInfo


class BaseSensorProvider(ABC):
    """Abstract interface for sensor telemetry acquisition (simulated or IoT/LoRa hardware)."""

    @abstractmethod
    def get_telemetry_for_scenario(self, scenario_id: str) -> Tuple[ScenarioInfo, Dict[str, SensorReading]]:
        pass


class DemoSensorProvider(BaseSensorProvider):
    """Deterministic simulation provider for live demo presentations."""

    SCENARIO_CONFIGS: Dict[str, Dict] = {
        "baseline": {
            "title": "Scenario A — Baseline Conditions",
            "description": "Normal dry/seasonal conditions. Stable ground tilt readings with low-to-moderate baseline soil saturation. Real forecast weather drives the atmospheric context.",
            "is_hypothetical_override": False,
            "simulated_rainfall_override_mm": None,
            "zones": {
                "zone_east_ridge": {
                    "node_id": "NODE-GKT-01",
                    "soil_moisture_vwc": 28.5,
                    "soil_moisture_status": "Normal / Moderate",
                    "tilt_degrees": 0.22,
                    "tilt_status": "Stable (Normal Creep)",
                    "battery_pct": 96,
                    "signal_rssi_dbm": -74,
                    "operational_status": "ONLINE",
                },
                "zone_ranipool_catchment": {
                    "node_id": "NODE-GKT-02",
                    "soil_moisture_vwc": 31.0,
                    "soil_moisture_status": "Normal / Moderate",
                    "tilt_degrees": 0.35,
                    "tilt_status": "Stable (Normal Creep)",
                    "battery_pct": 91,
                    "signal_rssi_dbm": -81,
                    "operational_status": "ONLINE",
                },
                "zone_tathangchen_slope": {
                    "node_id": "NODE-GKT-03",
                    "soil_moisture_vwc": 24.0,
                    "soil_moisture_status": "Dry / Well-Drained",
                    "tilt_degrees": 0.12,
                    "tilt_status": "Stable",
                    "battery_pct": 98,
                    "signal_rssi_dbm": -68,
                    "operational_status": "ONLINE",
                },
            },
        },
        "heavy_rain": {
            "title": "Scenario B — Heavy Rainfall + Wet Soil",
            "description": "Simulated monsoon deluge with 68.5 mm scenario precipitation override. Deep subsurface soil saturation across all slope monitoring nodes.",
            "is_hypothetical_override": True,
            "simulated_rainfall_override_mm": 68.5,
            "zones": {
                "zone_east_ridge": {
                    "node_id": "NODE-GKT-01",
                    "soil_moisture_vwc": 76.5,
                    "soil_moisture_status": "High Saturation",
                    "tilt_degrees": 1.15,
                    "tilt_status": "Accelerated Creep",
                    "battery_pct": 94,
                    "signal_rssi_dbm": -76,
                    "operational_status": "ONLINE",
                },
                "zone_ranipool_catchment": {
                    "node_id": "NODE-GKT-02",
                    "soil_moisture_vwc": 84.0,
                    "soil_moisture_status": "Critical Saturation",
                    "tilt_degrees": 1.45,
                    "tilt_status": "Accelerated Creep",
                    "battery_pct": 89,
                    "signal_rssi_dbm": -85,
                    "operational_status": "ONLINE",
                },
                "zone_tathangchen_slope": {
                    "node_id": "NODE-GKT-03",
                    "soil_moisture_vwc": 64.2,
                    "soil_moisture_status": "Elevated Moisture",
                    "tilt_degrees": 0.65,
                    "tilt_status": "Minor Creep",
                    "battery_pct": 97,
                    "signal_rssi_dbm": -71,
                    "operational_status": "ONLINE",
                },
            },
        },
        "tilt_anomaly": {
            "title": "Scenario C — Abnormal Tilt & Shear Anomaly",
            "description": "Acute mechanical displacement detected on critical highway sector node. Indicative of progressive shear failure along toe-cut slope.",
            "is_hypothetical_override": True,
            "simulated_rainfall_override_mm": 35.0,
            "zones": {
                "zone_east_ridge": {
                    "node_id": "NODE-GKT-01",
                    "soil_moisture_vwc": 58.0,
                    "soil_moisture_status": "Elevated Moisture",
                    "tilt_degrees": 1.85,
                    "tilt_status": "Active Creep",
                    "battery_pct": 93,
                    "signal_rssi_dbm": -77,
                    "operational_status": "ONLINE",
                },
                "zone_ranipool_catchment": {
                    "node_id": "NODE-GKT-02",
                    "soil_moisture_vwc": 74.0,
                    "soil_moisture_status": "Near Saturation",
                    "tilt_degrees": 4.35,  # Acute shear anomaly
                    "tilt_status": "CRITICAL TILT ANOMALY",
                    "battery_pct": 86,
                    "signal_rssi_dbm": -89,
                    "operational_status": "ONLINE",
                },
                "zone_tathangchen_slope": {
                    "node_id": "NODE-GKT-03",
                    "soil_moisture_vwc": 42.0,
                    "soil_moisture_status": "Moderate",
                    "tilt_degrees": 0.40,
                    "tilt_status": "Stable",
                    "battery_pct": 97,
                    "signal_rssi_dbm": -70,
                    "operational_status": "ONLINE",
                },
            },
        },
    }

    def get_available_scenarios(self) -> List[str]:
        return list(self.SCENARIO_CONFIGS.keys())

    def get_telemetry_for_scenario(self, scenario_id: str) -> Tuple[ScenarioInfo, Dict[str, SensorReading]]:
        if scenario_id not in self.SCENARIO_CONFIGS:
            scenario_id = "baseline"

        cfg = self.SCENARIO_CONFIGS[scenario_id]
        now_iso = datetime.now(timezone.utc).isoformat()

        scenario_info = ScenarioInfo(
            scenario_id=scenario_id,
            title=cfg["title"],
            description=cfg["description"],
            is_hypothetical_override=cfg["is_hypothetical_override"],
            simulated_rainfall_override_mm=cfg["simulated_rainfall_override_mm"],
        )

        readings: Dict[str, SensorReading] = {}
        for zone_id, zcfg in cfg["zones"].items():
            readings[zone_id] = SensorReading(
                node_id=zcfg["node_id"],
                zone_id=zone_id,
                timestamp=now_iso,
                is_simulated=True,
                data_source="SIMULATED",
                soil_moisture_vwc=zcfg["soil_moisture_vwc"],
                soil_moisture_status=zcfg["soil_moisture_status"],
                tilt_degrees=zcfg["tilt_degrees"],
                tilt_status=zcfg["tilt_status"],
                battery_pct=zcfg["battery_pct"],
                signal_rssi_dbm=zcfg["signal_rssi_dbm"],
                operational_status=zcfg["operational_status"],
            )

        return scenario_info, readings


# Singleton instance
sensor_provider = DemoSensorProvider()
