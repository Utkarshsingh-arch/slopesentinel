import React from 'react';
import { CloudRain, Activity, CheckCircle2, Sparkles } from 'lucide-react';
import { ScenarioInfo } from '../types';

interface ScenarioSelectorProps {
  currentScenario: ScenarioInfo;
  onSelectScenario: (scenarioId: 'baseline' | 'heavy_rain' | 'tilt_anomaly') => void;
  isLoading: boolean;
}

export const ScenarioSelector: React.FC<ScenarioSelectorProps> = ({
  currentScenario,
  onSelectScenario,
  isLoading,
}) => {
  const scenarios = [
    {
      id: 'baseline' as const,
      name: 'Scenario A: Baseline',
      subtitle: 'Normal Dry/Seasonal Conditions',
      icon: CheckCircle2,
      accent: 'border-slate-700 hover:border-slate-500',
      activeAccent: 'border-cyan-500 bg-cyan-950/30 text-cyan-300 ring-1 ring-cyan-500',
      badge: 'Live Context',
      badgeColor: 'bg-emerald-950/80 text-emerald-400 border-emerald-800',
      triggerText: 'Actual weather forecast & stable soil telemetry',
    },
    {
      id: 'heavy_rain' as const,
      name: 'Scenario B: Heavy Rainfall + Wet Soil',
      subtitle: 'Monsoon Surge + Soil Saturation',
      icon: CloudRain,
      accent: 'border-slate-700 hover:border-slate-500',
      activeAccent: 'border-amber-500 bg-amber-950/30 text-amber-300 ring-1 ring-amber-500',
      badge: '68.5mm Override',
      badgeColor: 'bg-amber-950/80 text-amber-400 border-amber-800',
      triggerText: 'Hypothetical 68.5mm rainfall + 84% VWC saturation',
    },
    {
      id: 'tilt_anomaly' as const,
      name: 'Scenario C: Abnormal Tilt',
      subtitle: 'Kinematic Shear Acceleration',
      icon: Activity,
      accent: 'border-slate-700 hover:border-slate-500',
      activeAccent: 'border-red-500 bg-red-950/30 text-red-300 ring-1 ring-red-500',
      badge: '4.35° Tilt Anomaly',
      badgeColor: 'bg-rose-950/80 text-rose-400 border-rose-800',
      triggerText: 'Acute displacement anomaly on Ranipool Flank node',
    },
  ];

  return (
    <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-4 shadow-lg">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-3 pb-2 border-b border-slate-800 gap-2">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">
            Interactive Scenario Selector
          </h2>
        </div>
        <span className="text-xs font-mono text-slate-400">
          Switch scenarios to trigger instant deterministic recalculation
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {scenarios.map((sc) => {
          const isSelected = currentScenario.scenario_id === sc.id;
          const Icon = sc.icon;

          return (
            <button
              key={sc.id}
              onClick={() => onSelectScenario(sc.id)}
              disabled={isLoading}
              className={`text-left p-3.5 rounded-lg border transition-all duration-200 flex flex-col justify-between ${
                isSelected
                  ? sc.activeAccent
                  : 'bg-slate-900/60 text-slate-300 ' + sc.accent
              } ${isLoading ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer hover:bg-slate-800/80'}`}
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <Icon className={`w-4 h-4 ${isSelected ? 'text-current' : 'text-slate-400'}`} />
                    <span className="font-semibold text-xs tracking-tight text-white">{sc.name}</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${sc.badgeColor}`}>
                    {sc.badge}
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-snug line-clamp-1">{sc.subtitle}</p>
              </div>

              <div className="mt-2.5 pt-2 border-t border-slate-800/80 text-[11px] text-slate-400 font-mono">
                {sc.triggerText}
              </div>
            </button>
          );
        })}
      </div>

      {/* Active Scenario Banner */}
      <div className="mt-3 px-3 py-2 rounded-lg bg-slate-900/90 border border-slate-800 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2 text-slate-300">
          <span className="font-semibold text-slate-200">Active Scenario:</span>
          <span>{currentScenario.title}</span>
        </div>
        {currentScenario.is_hypothetical_override && (
          <span className="text-[11px] text-amber-400 font-mono px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/60">
            Simulated Rainfall Override: {currentScenario.simulated_rainfall_override_mm} mm
          </span>
        )}
      </div>
    </div>
  );
};
