import React, { useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Polygon,
  Marker,
  Popup,
  useMap,
  Tooltip,
} from 'react-leaflet';
import L from 'leaflet';
import { Layers, Info } from 'lucide-react';
import { ZoneEvaluation, IllustrativeAsset } from '../types';

interface MapViewProps {
  zones: ZoneEvaluation[];
  assets: IllustrativeAsset[];
  selectedZoneId: string | null;
  onSelectZone: (zoneId: string) => void;
}

// Controller component to smoothly pan/zoom to selected zone
const MapController: React.FC<{ selectedZone: ZoneEvaluation | undefined }> = ({
  selectedZone,
}) => {
  const map = useMap();

  useEffect(() => {
    if (selectedZone) {
      map.flyTo(selectedZone.centroid, 14, {
        duration: 1.2,
      });
    }
  }, [selectedZone, map]);

  return null;
};

// Tactical pulsating marker icon for illustrative infrastructure assets
const createAssetIcon = (category: string) => {
  const color =
    category === 'road_corridor'
      ? '#06B6D4' // Cyan
      : category === 'critical_facility'
      ? '#F59E0B' // Amber
      : '#38BDF8'; // Sky Blue

  return L.divIcon({
    className: 'tactical-asset-pin',
    html: `
      <div style="position: relative; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center;">
        <span style="position: absolute; width: 16px; height: 16px; border-radius: 50%; background-color: ${color}; opacity: 0.4; animation: ping 1.8s cubic-bezier(0, 0, 0.2, 1) infinite;"></span>
        <span style="position: relative; width: 10px; height: 10px; border-radius: 50%; background-color: ${color}; border: 2px solid #ffffff; box-shadow: 0 0 6px ${color};"></span>
      </div>
    `,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
};

export const MapView: React.FC<MapViewProps> = ({
  zones,
  assets,
  selectedZoneId,
  onSelectZone,
}) => {
  const gangtokCenter: [number, number] = [27.3389, 88.6065];
  const selectedZone = zones.find((z) => z.zone_id === selectedZoneId);

  // Status color mapper
  const getZoneColor = (level: string, isSelected: boolean) => {
    switch (level) {
      case 'Critical':
        return {
          fillColor: '#EF4444',
          color: isSelected ? '#FFFFFF' : '#DC2626',
          weight: isSelected ? 3 : 2,
          fillOpacity: isSelected ? 0.65 : 0.45,
        };
      case 'Elevated':
        return {
          fillColor: '#F59E0B',
          color: isSelected ? '#FFFFFF' : '#D97706',
          weight: isSelected ? 3 : 2,
          fillOpacity: isSelected ? 0.6 : 0.4,
        };
      case 'Watch':
        return {
          fillColor: '#06B6D4',
          color: isSelected ? '#FFFFFF' : '#0891B2',
          weight: isSelected ? 3 : 2,
          fillOpacity: isSelected ? 0.55 : 0.35,
        };
      case 'Low':
      default:
        return {
          fillColor: '#10B981',
          color: isSelected ? '#FFFFFF' : '#059669',
          weight: isSelected ? 3 : 2,
          fillOpacity: isSelected ? 0.5 : 0.3,
        };
    }
  };

  return (
    <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col h-full min-h-[520px]">
      {/* Map Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-3 border-b border-slate-800 gap-2">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
            Geospatial Intelligence Map &bull; Gangtok Sector
          </h3>
        </div>
        <div className="text-[11px] font-mono text-slate-400">
          OpenStreetMap &bull; EPSG:3857 &bull; Gangtok [27.3389°N, 88.6065°E]
        </div>
      </div>

      {/* Map Canvas */}
      <div className="relative flex-1 mt-3 rounded-lg overflow-hidden border border-slate-800">
        <MapContainer
          center={gangtokCenter}
          zoom={13}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%', minHeight: '440px' }}
        >
          {/* Base OpenStreetMap TileLayer with required attribution */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            className="tactical-tiles"
          />

          <MapController selectedZone={selectedZone} />

          {/* Illustrative Zone Polygons */}
          {zones.map((zone) => {
            const isSelected = selectedZoneId === zone.zone_id;
            const style = getZoneColor(zone.status_level, isSelected);

            // Leaflet requires [lat, lon] tuples; GeoJSON stores [lon, lat]
            const positions: [number, number][] = zone.geometry.coordinates[0].map(
              ([lon, lat]) => [lat, lon]
            );

            return (
              <Polygon
                key={zone.zone_id}
                positions={positions}
                pathOptions={style}
                eventHandlers={{
                  click: () => onSelectZone(zone.zone_id),
                }}
              >
                <Tooltip direction="top" offset={[0, -10]} opacity={0.95}>
                  <div className="font-sans text-xs">
                    <span className="font-bold text-slate-900 block">{zone.zone_name}</span>
                    <span className="text-[10px] text-slate-700 font-mono">
                      Priority: {zone.priority_score.toFixed(1)} &bull; {zone.status_level}
                    </span>
                  </div>
                </Tooltip>

                <Popup>
                  <div className="p-1 space-y-2 max-w-xs text-xs">
                    <div className="flex items-center justify-between border-b border-slate-700 pb-1.5">
                      <span className="font-bold text-cyan-300 text-sm">{zone.zone_name}</span>
                      <span
                        className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold ${
                          zone.status_level === 'Critical'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : zone.status_level === 'Elevated'
                            ? 'bg-amber-950 text-amber-300 border border-amber-800'
                            : zone.status_level === 'Watch'
                            ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                            : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        }`}
                      >
                        Rank #{zone.priority_rank} &bull; {zone.status_level}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-1.5 text-[11px] font-mono">
                      <div className="bg-slate-900 p-1.5 rounded border border-slate-800">
                        <span className="text-slate-400 block text-[10px]">Priority Score</span>
                        <span className="text-white font-bold text-sm">
                          {zone.priority_score.toFixed(1)}/100
                        </span>
                      </div>
                      <div className="bg-slate-900 p-1.5 rounded border border-slate-800">
                        <span className="text-slate-400 block text-[10px]">Risk Index</span>
                        <span className="text-white font-bold text-sm">
                          {zone.risk_index.toFixed(1)}/100
                        </span>
                      </div>
                    </div>

                    <div>
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                        Strongest Contributing Factors:
                      </span>
                      <ul className="list-disc list-inside text-[11px] text-slate-300 space-y-0.5">
                        {zone.contributing_factors.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="p-1.5 bg-slate-900 rounded border border-slate-800 text-[10px]">
                      <span className="font-semibold text-slate-300">Action: </span>
                      <span className="text-slate-400">{zone.response_recommendation}</span>
                    </div>

                    <div className="text-[9px] text-amber-400/80 italic pt-1 border-t border-slate-800">
                      Illustrative scenario region &bull; Not an official GSI hazard boundary
                    </div>
                  </div>
                </Popup>
              </Polygon>
            );
          })}

          {/* Illustrative Infrastructure Asset Markers */}
          {assets.map((asset) => (
            <Marker
              key={asset.asset_id}
              position={[asset.coordinates[1], asset.coordinates[0]]}
              icon={createAssetIcon(asset.category)}
            >
              <Popup>
                <div className="p-1 text-xs">
                  <div className="font-bold text-white mb-1 flex items-center space-x-1">
                    <Info className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{asset.name}</span>
                  </div>
                  <p className="text-[11px] text-slate-300 mb-1.5">{asset.description}</p>
                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800">
                    <span>Category: {asset.category}</span>
                    <span className="text-amber-400">Exposure: {asset.exposure_rating}/100</span>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Legend Overlay */}
        <div className="absolute bottom-3 left-3 z-[400] bg-slate-900/90 backdrop-blur-md p-3 rounded-lg border border-slate-800 shadow-xl text-xs max-w-xs pointer-events-auto">
          <div className="font-bold text-slate-200 text-[11px] uppercase tracking-wider mb-1.5 flex items-center justify-between">
            <span>Response Urgency Tiers</span>
          </div>

          <div className="grid grid-cols-2 gap-1.5 text-[10px] font-mono">
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded bg-red-500/80 border border-red-400 inline-block" />
              <span className="text-slate-300">Critical (&ge;75)</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded bg-amber-500/80 border border-amber-400 inline-block" />
              <span className="text-slate-300">Elevated (55-74)</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded bg-cyan-500/80 border border-cyan-400 inline-block" />
              <span className="text-slate-300">Watch (30-54)</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded bg-emerald-500/80 border border-emerald-400 inline-block" />
              <span className="text-slate-300">Low (&lt;30)</span>
            </div>
          </div>

          <p className="text-[9px] text-amber-400/90 mt-2 pt-1.5 border-t border-slate-800 leading-tight">
            Polygons represent illustrative scenario demo zones, not certified GSI landslide hazard perimeters.
          </p>
        </div>
      </div>
    </div>
  );
};
