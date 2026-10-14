import React from 'react';
import { Shield, Database, Cpu, Map, AlertTriangle } from 'lucide-react';
import { DataProvenance, SiteMeta } from '../types';

interface ProvenanceFooterProps {
  provenance?: DataProvenance;
  meta?: SiteMeta;
}

export const ProvenanceFooter: React.FC<ProvenanceFooterProps> = ({ provenance, meta }) => {
  return (
    <footer className="mt-8 bg-[#0F172A] border-t border-slate-800 p-4 sm:p-6 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto space-y-4">
        {/* Core Disclaimer Callout */}
        <div className="p-3.5 rounded-lg bg-amber-950/30 border border-amber-800/40 text-amber-300 text-xs flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-amber-200">
              DISCLAIMER &bull; DEMONSTRATION INTELLIGENCE PLATFORM ONLY
            </span>
            <p className="text-[11px] text-amber-400/90 leading-relaxed">
              {meta?.disclaimer ||
                'SlopeSentinel is an academic and technical prototype. Risk indices and response-priority scores are calculated using a deterministic demonstration heuristic and illustrative exposure values. They do NOT represent certified geological hazard warnings or calibrated landslide probabilities.'}
            </p>
          </div>
        </div>

        {/* Provenance Metadata Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-2">
          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <div className="flex items-center space-x-1.5 text-slate-300 font-semibold mb-1">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span>Weather Source</span>
            </div>
            <div className="font-mono text-[11px] text-cyan-300">
              {provenance?.weather_source || 'Open-Meteo REST API'}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Status: <span className="font-mono uppercase">{provenance?.weather_status || 'live'}</span>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <div className="flex items-center space-x-1.5 text-slate-300 font-semibold mb-1">
              <Cpu className="w-3.5 h-3.5 text-teal-400" />
              <span>Sensor Telemetry</span>
            </div>
            <div className="font-mono text-[11px] text-teal-300">
              {provenance?.sensor_mode || 'SIMULATED'}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Deterministic scenario model
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <div className="flex items-center space-x-1.5 text-slate-300 font-semibold mb-1">
              <Map className="w-3.5 h-3.5 text-blue-400" />
              <span>Geospatial Data</span>
            </div>
            <div className="font-mono text-[11px] text-blue-300">
              {provenance?.zones_mode || 'ILLUSTRATIVE_DEMO_DATA'}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Basemap: &copy; OpenStreetMap
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <div className="flex items-center space-x-1.5 text-slate-300 font-semibold mb-1">
              <Shield className="w-3.5 h-3.5 text-indigo-400" />
              <span>Risk Formulation</span>
            </div>
            <div className="font-mono text-[11px] text-indigo-300">
              {provenance?.algorithm_notice || 'DETERMINISTIC_HEURISTIC'}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Normalized component weighting
            </div>
          </div>
        </div>

        {/* Footer Copyright and Timestamp */}
        <div className="pt-2 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 gap-2">
          <div>
            SlopeSentinel &bull; Regional Landslide Intelligence Platform &bull; Gangtok, Sikkim, India
          </div>
          <div className="font-mono text-[10px]">
            {meta?.evaluated_at ? `Evaluated At: ${new Date(meta.evaluated_at).toUTCString()}` : ''}
          </div>
        </div>
      </div>
    </footer>
  );
};
