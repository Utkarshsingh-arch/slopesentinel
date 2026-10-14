import React from 'react';
import { Cloud, Droplets, Wind, Thermometer, Clock, Database } from 'lucide-react';
import { WeatherData } from '../types';

interface WeatherCardProps {
  weather: WeatherData;
  scenarioOverrideMm: number | null;
}

export const WeatherCard: React.FC<WeatherCardProps> = ({ weather, scenarioOverrideMm }) => {
  const getStatusBadge = () => {
    switch (weather.source_status) {
      case 'live':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-emerald-950/80 text-emerald-300 border border-emerald-800">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse" />
            LIVE OBSERVATION
          </span>
        );
      case 'cached':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-blue-950/80 text-blue-300 border border-blue-800">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mr-1.5" />
            CACHED (15m TTL)
          </span>
        );
      case 'fallback':
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-amber-950/80 text-amber-300 border border-amber-800">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mr-1.5" />
            OFFLINE FALLBACK
          </span>
        );
    }
  };

  return (
    <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Cloud className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Atmospheric Context
            </h3>
          </div>
          {getStatusBadge()}
        </div>

        {/* Current Condition & Temp */}
        <div className="mt-3 flex items-baseline justify-between">
          <div>
            <div className="text-2xl font-extrabold text-white font-mono">
              {weather.temperature_c.toFixed(1)}°C
            </div>
            <div className="text-xs text-cyan-300 font-medium">{weather.condition_text}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400">Feels Like</div>
            <div className="text-sm font-mono text-slate-200">
              {weather.apparent_temperature_c.toFixed(1)}°C
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-2 mt-4">
          <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="flex items-center text-[11px] text-slate-400 mb-0.5">
              <Droplets className="w-3 h-3 mr-1 text-cyan-400" />
              Observed Precip
            </div>
            <div className="text-sm font-mono font-bold text-white">
              {weather.current_precipitation_mm.toFixed(1)} mm
            </div>
          </div>

          <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="flex items-center text-[11px] text-slate-400 mb-0.5">
              <Droplets className="w-3 h-3 mr-1 text-blue-400" />
              24h Forecast Precip
            </div>
            <div className="text-sm font-mono font-bold text-white">
              {weather.forecast_24h_precip_mm.toFixed(1)} mm
            </div>
          </div>

          <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="flex items-center text-[11px] text-slate-400 mb-0.5">
              <Thermometer className="w-3 h-3 mr-1 text-teal-400" />
              Rel Humidity
            </div>
            <div className="text-sm font-mono font-bold text-white">
              {weather.relative_humidity_pct.toFixed(0)}%
            </div>
          </div>

          <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800">
            <div className="flex items-center text-[11px] text-slate-400 mb-0.5">
              <Wind className="w-3 h-3 mr-1 text-slate-400" />
              Wind Speed
            </div>
            <div className="text-sm font-mono font-bold text-white">
              {weather.wind_speed_kmh.toFixed(1)} km/h
            </div>
          </div>
        </div>

        {/* Hypothetical Override Display */}
        {scenarioOverrideMm !== null && (
          <div className="mt-3 p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/60 text-xs">
            <div className="flex items-center justify-between font-semibold text-amber-300">
              <span>Scenario Trigger Override:</span>
              <span className="font-mono text-amber-400">{scenarioOverrideMm.toFixed(1)} mm</span>
            </div>
            <p className="text-[11px] text-amber-400/80 mt-1">
              Separately injected hypothetical rainfall for risk engine trigger simulation.
            </p>
          </div>
        )}
      </div>

      {/* Footer / Provenance */}
      <div className="mt-4 pt-2.5 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
        <div className="flex items-center space-x-1">
          <Database className="w-3 h-3 text-slate-400" />
          <span>Source: {weather.source}</span>
        </div>
        <div className="flex items-center space-x-1 font-mono text-[10px]">
          <Clock className="w-3 h-3 text-slate-400" />
          <span>{new Date(weather.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
      </div>
    </div>
  );
};
