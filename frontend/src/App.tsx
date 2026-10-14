import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { ScenarioSelector } from './components/ScenarioSelector';
import { WeatherCard } from './components/WeatherCard';
import { SensorPanel } from './components/SensorPanel';
import { MapView } from './components/MapView';
import { PriorityList } from './components/PriorityList';
import { ProvenanceFooter } from './components/ProvenanceFooter';
import { fetchDashboardData } from './services/api';
import { DashboardPayload } from './types';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [scenario, setScenario] = useState<'baseline' | 'heavy_rain' | 'tilt_anomaly'>('baseline');
  const [data, setData] = useState<DashboardPayload | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedZoneId, setSelectedZoneId] = useState<string | null>(null);

  const loadData = useCallback(async (scenarioId: string, refresh: boolean = false) => {
    if (refresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      const payload = await fetchDashboardData(scenarioId, refresh);
      setData(payload);
      // Default to rank 1 zone if none selected
      if (payload.zones && payload.zones.length > 0) {
        setSelectedZoneId((prev) => (prev ? prev : payload.zones[0].zone_id));
      }
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError(
        err.message || 'Unable to connect to SlopeSentinel backend API. Ensure backend is running on :8000.'
      );
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData(scenario, false);
  }, [scenario, loadData]);

  const handleScenarioChange = (newScenario: 'baseline' | 'heavy_rain' | 'tilt_anomaly') => {
    if (newScenario !== scenario) {
      setScenario(newScenario);
    }
  };

  const handleRefresh = () => {
    loadData(scenario, true);
  };

  return (
    <div className="min-h-screen bg-[#0A0F1D] flex flex-col justify-between">
      <div>
        {/* Navigation & Status Header */}
        <Header
          meta={data?.meta}
          isRefreshing={isRefreshing}
          onRefresh={handleRefresh}
        />

        <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 space-y-6">
          {/* Error Alert Banner */}
          {error && (
            <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-700 text-rose-200 flex items-start justify-between gap-3 shadow-lg">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-sm">Dashboard Service Connection Warning</h4>
                  <p className="text-xs text-rose-300 mt-1">{error}</p>
                </div>
              </div>
              <button
                onClick={() => loadData(scenario, false)}
                className="px-3 py-1.5 rounded-lg bg-rose-800 hover:bg-rose-700 text-white text-xs font-semibold shrink-0 transition"
              >
                Retry Request
              </button>
            </div>
          )}

          {/* Scenario Selector */}
          {data && (
            <ScenarioSelector
              currentScenario={data.scenario}
              onSelectScenario={handleScenarioChange}
              isLoading={isLoading}
            />
          )}

          {/* Loading State Overlay / Skeleton */}
          {isLoading && !data && (
            <div className="flex flex-col items-center justify-center p-16 space-y-4">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
              <div className="text-sm text-slate-300 font-mono">
                Ingesting Open-Meteo context and evaluating Gangtok slope zones...
              </div>
            </div>
          )}

          {/* Main Dashboard Layout */}
          {data && (
            <div className="space-y-6">
              {/* Top Row: Environmental Context + Telemetry */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <WeatherCard
                  weather={data.weather}
                  scenarioOverrideMm={data.scenario.simulated_rainfall_override_mm}
                />
                <SensorPanel
                  sensors={data.sensors}
                  zones={data.zones}
                  selectedZoneId={selectedZoneId}
                  onSelectZone={setSelectedZoneId}
                />
              </div>

              {/* Bottom Row: Geospatial Map + Response Priority Ranked List */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-7 h-[540px]">
                  <MapView
                    zones={data.zones}
                    assets={data.illustrative_assets}
                    selectedZoneId={selectedZoneId}
                    onSelectZone={setSelectedZoneId}
                  />
                </div>

                <div className="lg:col-span-5">
                  <PriorityList
                    zones={data.zones}
                    selectedZoneId={selectedZoneId}
                    onSelectZone={setSelectedZoneId}
                  />
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Provenance & Disclaimers Footer */}
      <ProvenanceFooter provenance={data?.data_provenance} meta={data?.meta} />
    </div>
  );
};

export default App;
