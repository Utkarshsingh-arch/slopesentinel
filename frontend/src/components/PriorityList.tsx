import React from 'react';
import { AlertCircle, TrendingUp, MapPin } from 'lucide-react';
import { ZoneEvaluation } from '../types';

interface PriorityListProps {
  zones: ZoneEvaluation[];
  selectedZoneId: string | null;
  onSelectZone: (zoneId: string) => void;
}

export const PriorityList: React.FC<PriorityListProps> = ({
  zones,
  selectedZoneId,
  onSelectZone,
}) => {
  const getBadgeStyle = (level: string) => {
    switch (level) {
      case 'Critical':
        return 'bg-rose-950/90 text-rose-300 border-rose-800 ring-1 ring-rose-500/50';
      case 'Elevated':
        return 'bg-amber-950/90 text-amber-300 border-amber-800';
      case 'Watch':
        return 'bg-cyan-950/90 text-cyan-300 border-cyan-800';
      case 'Low':
      default:
        return 'bg-emerald-950/90 text-emerald-300 border-emerald-800';
    }
  };

  return (
    <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Response-Priority Ranking
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Ranked by Urgency Score
          </span>
        </div>

        <p className="text-xs text-slate-400 mt-2 mb-3">
          Synthesizes geotechnical risk index (65%) with infrastructure exposure (35%). Click any card to spotlight on map.
        </p>

        {/* Zones List */}
        <div className="space-y-3">
          {zones.map((zone) => {
            const isSelected = selectedZoneId === zone.zone_id;

            return (
              <div
                key={zone.zone_id}
                onClick={() => onSelectZone(zone.zone_id)}
                className={`p-3.5 rounded-lg border transition cursor-pointer relative ${
                  isSelected
                    ? 'border-cyan-400 bg-slate-800/90 shadow-md ring-1 ring-cyan-500/40'
                    : 'border-slate-800 bg-slate-900/60 hover:bg-slate-800/50'
                }`}
              >
                {/* Top Row: Rank & Name */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center space-x-2.5">
                    <span className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-mono font-bold text-xs text-cyan-300">
                      #{zone.priority_rank}
                    </span>
                    <div>
                      <h4 className="font-bold text-sm text-white flex items-center space-x-1.5">
                        <span>{zone.zone_name}</span>
                      </h4>
                      <span className="text-[11px] font-mono text-slate-400 flex items-center">
                        <MapPin className="w-3 h-3 mr-0.5 text-slate-400" />
                        {zone.zone_id}
                      </span>
                    </div>
                  </div>

                  <span
                    className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold border ${getBadgeStyle(
                      zone.status_level
                    )}`}
                  >
                    {zone.status_level.toUpperCase()}
                  </span>
                </div>

                {/* Scores Matrix */}
                <div className="grid grid-cols-3 gap-2 mt-3 pt-2 border-t border-slate-800/80 text-center font-mono">
                  <div className="p-1.5 bg-slate-950/70 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase">Priority</div>
                    <div className="text-base font-extrabold text-white">
                      {zone.priority_score.toFixed(1)}
                    </div>
                  </div>
                  <div className="p-1.5 bg-slate-950/70 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase">Risk Index</div>
                    <div className="text-base font-bold text-cyan-300">
                      {zone.risk_index.toFixed(1)}
                    </div>
                  </div>
                  <div className="p-1.5 bg-slate-950/70 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase">Exposure</div>
                    <div className="text-base font-bold text-amber-300">
                      {zone.exposure_score.toFixed(0)}
                    </div>
                  </div>
                </div>

                {/* Contributing Triggers */}
                <div className="mt-2.5">
                  <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    Strongest Contributing Factors:
                  </div>
                  <ul className="text-xs text-slate-300 space-y-1">
                    {zone.contributing_factors.map((factor, i) => (
                      <li key={i} className="flex items-start space-x-1.5 text-[11px]">
                        <span className="text-cyan-400 font-bold">&bull;</span>
                        <span className="text-slate-300">{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Exposed Assets */}
                <div className="mt-2 text-[11px] text-slate-400">
                  <span className="text-slate-400 font-semibold">Exposed Infrastructure: </span>
                  <span className="text-slate-300">{zone.exposed_assets.join(', ')}</span>
                </div>

                {/* Recommendation */}
                <div className="mt-2.5 p-2 rounded bg-slate-950/90 border border-slate-800 text-[11px] text-slate-300 flex items-start space-x-1.5">
                  <AlertCircle className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                  <span>{zone.response_recommendation}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 pt-2.5 border-t border-slate-800 text-[10px] text-slate-400 text-center font-mono">
        SCORES REPRESENT DECISION SUPPORT RANKING &bull; NOT SCIENTIFIC FAILURE PROBABILITY
      </div>
    </div>
  );
};
