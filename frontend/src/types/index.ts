export type OperationalStatusLevel = 'Low' | 'Watch' | 'Elevated' | 'Critical';
export type WeatherSourceStatus = 'live' | 'cached' | 'fallback';

export interface WeatherData {
  source: string;
  source_status: WeatherSourceStatus;
  timestamp: string;
  temperature_c: number;
  relative_humidity_pct: number;
  apparent_temperature_c: number;
  current_precipitation_mm: number;
  forecast_24h_precip_mm: number;
  wind_speed_kmh: number;
  weather_code: number;
  condition_text: string;
  is_fallback: boolean;
  notes?: string;
}

export interface SensorReading {
  node_id: string;
  zone_id: string;
  timestamp: string;
  is_simulated: boolean;
  data_source: string;
  soil_moisture_vwc: number;
  soil_moisture_status: string;
  tilt_degrees: number;
  tilt_status: string;
  battery_pct: number;
  signal_rssi_dbm: number;
  operational_status: 'ONLINE' | 'DEGRADED' | 'OFFLINE';
}

export interface RiskComponents {
  susceptibility_score: number;
  rainfall_score: number;
  soil_moisture_score: number;
  tilt_score: number;
}

export interface GeoPolygon {
  type: 'Polygon';
  coordinates: number[][][]; // GeoJSON [lon, lat]
}

export interface IllustrativeAsset {
  asset_id: string;
  name: string;
  category: 'road_corridor' | 'settlement' | 'critical_facility' | 'transit_hub';
  description: string;
  exposure_rating: number;
  coordinates: [number, number]; // [lon, lat]
}

export interface ZoneEvaluation {
  zone_id: string;
  zone_name: string;
  description: string;
  centroid: [number, number]; // [lat, lon]
  geometry: GeoPolygon;
  baseline_susceptibility: number;
  exposure_score: number;
  exposed_assets: string[];
  sensor_telemetry: SensorReading;
  risk_components: RiskComponents;
  risk_index: number;
  priority_score: number;
  priority_rank: number;
  status_level: OperationalStatusLevel;
  contributing_factors: string[];
  response_recommendation: string;
  provenance_notice: string;
}

export interface ScenarioInfo {
  scenario_id: 'baseline' | 'heavy_rain' | 'tilt_anomaly';
  title: string;
  description: string;
  is_hypothetical_override: boolean;
  simulated_rainfall_override_mm: number | null;
}

export interface SiteMeta {
  site_id: string;
  site_name: string;
  region: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
  evaluated_at: string;
  disclaimer: string;
  is_official_warning: boolean;
}

export interface DataProvenance {
  weather_source: string;
  weather_status: WeatherSourceStatus;
  sensor_mode: string;
  zones_mode: string;
  algorithm_notice: string;
}

export interface DashboardPayload {
  meta: SiteMeta;
  scenario: ScenarioInfo;
  weather: WeatherData;
  sensors: SensorReading[];
  zones: ZoneEvaluation[];
  illustrative_assets: IllustrativeAsset[];
  data_provenance: DataProvenance;
}
