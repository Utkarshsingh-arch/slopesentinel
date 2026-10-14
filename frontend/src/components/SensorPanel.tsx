import React from 'react';
import { Cpu, Wifi, Battery, Gauge, Compass } from 'lucide-react';
import { SensorReading, ZoneEvaluation } from '../types';

interface SensorPanelProps {
  sensors: SensorReading[];
  zones: ZoneEvaluation[];
  selectedZoneId: string | null;
  onSelectZone: (zoneId: string) => void;
}

export const SensorPanel: React.FC<SensorPanelProps> = ({
  sensors,
  zones,
  selectedZoneId,
  onSelectZone,
}) => {
  // Map zone_id to zone_name
  const zoneNameMap = zones.reduce((acc, z) => {
    acc[z.zone_id] = z.zone_name;
    return acc;
  }, {} as Record<string, string>);

  return (
    <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between">
      <div>
        {/* Header with SIMULATED BADGE */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Ground Sensor Telemetry
            </h3>
          </div>
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-amber-950/80 text-amber-400 border border-amber-800">
            SIMULATED
          </span>
        </div>

        <p className="text-xs text-slate-400 mt-2">
          Deterministic synthetic readings for geotechnical biaxial tilt &amp; volumetric soil moisture.
        </p>

        {/* Nodes Grid */}
        <div className="space-y-2.5 mt-3">
          {sensors.map((sensor) => {
            const isSelected = selectedZoneId === sensor.zone_id;
            const zoneName = zoneNameMap[sensor.zone_id] || sensor.zone_id;
            const isCriticalTilt = sensor.tilt_degrees >= 3.0;
            const isHighMoisture = sensor.soil_moisture_vwc >= 75.0;

            return (
              <div
                key={sensor.node_id}
                onClick={() => onSelectZone(sensor.zone_id)}
                className={`p-3 rounded-lg border transition cursor-pointer ${
                  isSelected
                    ? 'border-cyan-500 bg-slate-800/90 ring-1 ring-cyan-500/40'
                    : 'border-slate-800 bg-slate-900/60 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold text-cyan-300">
                      {sensor.node_id}
                    </span>
                    <span className="text-xs text-slate-300 font-medium truncate max-w-[140px]">
                      {zoneName}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400">
                    <span className="flex items-center">
                      <Wifi className="w-2.5 h-2.5 mr-0.5 text-slate-400" />
                      {sensor.signal_rssi_dbm}dBm
                    </span>
                    <span className="flex items-center">
                      <Battery className="w-2.5 h-2.5 mr-0.5 text-emerald-400" />
                      {sensor.battery_pct}%
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  {/* Moisture */}
                  <div className="p-1.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <div className="text-[10px] text-slate-400 flex items-center justify-between">
                      <span className="flex items-center">
                        <Gauge className="w-2.5 h-2.5 mr-1 text-cyan-400" />
                        Soil Moisture
                      </span>
                      <span className={isHighMoisture ? 'text-amber-400 font-bold' : 'text-slate-400'}>
                        {sensor.soil_moisture_status}
                      </span>
                    </div>
                    <div className="font-mono font-bold text-sm text-white mt-0.5">
                      {sensor.soil_moisture_vwc.toFixed(1)}% VWC
                    </div>
                  </div>

                  {/* Tilt */}
                  <div className="p-1.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <div className="text-[10px] text-slate-400 flex items-center justify-between">
                      <span className="flex items-center">
                        <Compass className="w-2.5 h-2.5 mr-1 text-teal-400" />
                        Slope Tilt
                      </span>
                      <span className={isCriticalTilt ? 'text-rose-400 font-bold' : 'text-slate-400'}>
                        {isCriticalTilt ? 'CRITICAL' : sensor.tilt_status}
                      </span>
                    </div>
                    <div className={`font-mono font-bold text-sm mt-0.5 ${isCriticalTilt ? 'text-rose-400' : 'text-white'}`}>
                      {sensor.tilt_degrees.toFixed(2)}°
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-400 text-center font-mono">
        NO PHYSICAL SENSORS CONNECTED &bull; SIMULATED TELEMETRY HARNESS
      </div>
    </div>
  );
};
