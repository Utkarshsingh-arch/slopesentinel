import React from 'react';
import { ShieldAlert, RefreshCw, Radio, Compass } from 'lucide-react';
import { SiteMeta } from '../types';

interface HeaderProps {
  meta?: SiteMeta;
  isRefreshing: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ meta, isRefreshing, onRefresh }) => {
  return (
    <header className="bg-[#0F172A] border-b border-slate-800 sticky top-0 z-50 px-4 py-3 sm:px-6 shadow-xl">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        {/* Left: Branding */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-600 to-teal-400 flex items-center justify-center shadow-lg shadow-cyan-900/30">
            <Radio className="w-6 h-6 text-slate-950 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center">
                SlopeSentinel
                <span className="ml-2 text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                  v1.0-MVP
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Regional Landslide Intelligence & Response Prioritization
            </p>
          </div>
        </div>

        {/* Center: MANDATORY DEMO NOTICE BADGE */}
        <div className="flex items-center px-3 py-1.5 rounded-full bg-amber-950/40 border border-amber-600/40 text-amber-300 text-xs font-semibold space-x-2 shadow-inner">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
          <span>DEMO PROTOTYPE &bull; NOT AN OFFICIAL GSI / GOVERNMENT WARNING</span>
        </div>

        {/* Right: Site & Controls */}
        <div className="flex items-center space-x-3 w-full md:w-auto justify-between md:justify-end">
          <div className="text-right hidden sm:block">
            <div className="text-xs font-semibold text-slate-200 flex items-center justify-end space-x-1">
              <Compass className="w-3.5 h-3.5 text-cyan-400" />
              <span>{meta?.site_name || 'Gangtok Pilot Sector'}</span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono">
              {meta ? `${meta.latitude.toFixed(4)}°N, ${meta.longitude.toFixed(4)}°E` : '27.3389°N, 88.6065°E'}
            </div>
          </div>

          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-slate-200 border border-slate-700 transition disabled:opacity-50"
            title="Force refresh live weather retrieval"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-cyan-400' : 'text-slate-400'}`} />
            <span>{isRefreshing ? 'Polling...' : 'Refresh Weather'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
