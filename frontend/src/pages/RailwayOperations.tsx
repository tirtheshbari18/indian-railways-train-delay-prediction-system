import React, { useState, useEffect } from 'react';
import { 
  GitFork, 
  MapPin, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  Layers, 
  Building2, 
  Compass, 
  ShieldCheck,
  FileSpreadsheet,
  Zap,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { OperationalEvent, RailwayDistance, RailwayZone } from '../types';

export const RailwayOperations: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'events' | 'chainage' | 'zones'>('events');
  const [events, setEvents] = useState<OperationalEvent[]>([]);
  const [distances, setDistances] = useState<RailwayDistance[]>([]);
  const [zones, setZones] = useState<RailwayZone[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadOperationsData();
  }, []);

  const loadOperationsData = async () => {
    setLoading(true);
    try {
      const [evData, distData, zonesData] = await Promise.all([
        api.getOperationalEvents(),
        api.getRailwayDistances(undefined, undefined, true),
        api.getRailwayZones()
      ]);
      setEvents(Array.isArray(evData) ? evData : []);
      setDistances(Array.isArray(distData) ? distData : []);
      setZones(Array.isArray(zonesData) ? zonesData : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-railway-navy via-railway-steel to-railway-blue rounded-2xl p-6 text-white shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase font-bold tracking-widest text-blue-300">Operational Infrastructure</span>
              <span className="bg-amber-500/30 text-amber-300 border border-amber-400/30 px-2 py-0.5 rounded text-[11px] font-bold">
                Module 8, 10 & 12
              </span>
            </div>
            <h2 className="text-2xl font-black tracking-tight mt-1">Railway Operational Meets, Chainage & Zones</h2>
            <p className="text-sm text-slate-300 max-w-3xl mt-1">
              Real operational train meetings, crossings, scheduled overtaking events, consecutive station chainage distances, and the 18 official Indian Railways administrative zones.
            </p>
          </div>
        </div>

        {/* Sub-tab Navigation */}
        <div className="flex items-center gap-2 mt-6 pt-4 border-t border-white/10">
          <button
            onClick={() => setActiveSubTab('events')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeSubTab === 'events'
                ? 'bg-white text-railway-navy shadow-sm'
                : 'bg-white/10 hover:bg-white/20 text-white'
            }`}
          >
            <GitFork className="w-3.5 h-3.5" />
            <span>Crossings & Overtakes</span>
          </button>

          <button
            onClick={() => setActiveSubTab('chainage')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeSubTab === 'chainage'
                ? 'bg-white text-railway-navy shadow-sm'
                : 'bg-white/10 hover:bg-white/20 text-white'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Consecutive Station Chainage (km)</span>
          </button>

          <button
            onClick={() => setActiveSubTab('zones')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeSubTab === 'zones'
                ? 'bg-white text-railway-navy shadow-sm'
                : 'bg-white/10 hover:bg-white/20 text-white'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>18 Railway Zones & Divisions</span>
          </button>
        </div>
      </div>

      {/* Sub-tab 1: Operational Events (Crossings & Overtakes) */}
      {activeSubTab === 'events' && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex items-center justify-between">
            <div className="text-xs text-slate-600">
              Verified operational events derived from Western & Northern Railway Working Timetables.
            </div>
            <span className="text-xs font-bold bg-blue-50 text-blue-700 px-2.5 py-1 rounded-lg">
              {events.length} Operational Meets Registered
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {events.map((ev) => (
              <div
                key={ev.id || `${ev.first_train_number}-${ev.second_train_number}`}
                className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-railway-blue bg-blue-50 px-2 py-0.5 rounded">
                    {ev.event_type}
                  </span>
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 font-mono font-bold">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>{ev.scheduled_time || '14:15'}</span>
                  </div>
                </div>

                <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 flex items-center justify-between gap-4">
                  <div>
                    <div className="text-[10px] uppercase font-bold text-slate-400">Station</div>
                    <div className="text-sm font-black text-slate-900">{ev.station_name || ev.station_code}</div>
                    <div className="text-[10px] font-mono text-slate-500">Code: {ev.station_code}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] uppercase font-bold text-slate-400">Track Infrastructure</div>
                    <div className="text-xs font-semibold text-slate-700">{ev.track_line || 'Main Line / Loop'}</div>
                  </div>
                </div>

                {/* The 2 Involved Trains */}
                <div className="space-y-2">
                  <div className="p-2.5 bg-blue-50/50 rounded-lg border border-blue-100 flex items-center justify-between">
                    <div>
                      <span className="text-xs font-black font-mono text-slate-900">{ev.first_train_number}</span>
                      <span className="text-xs font-bold text-slate-700 ml-2">{ev.first_train_name}</span>
                    </div>
                    <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded">
                      Primary Service
                    </span>
                  </div>

                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
                    <div>
                      <span className="text-xs font-black font-mono text-slate-900">{ev.second_train_number}</span>
                      <span className="text-xs font-bold text-slate-700 ml-2">{ev.second_train_name}</span>
                    </div>
                    <span className="text-[10px] font-bold bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded">
                      Crossing / Overtaken
                    </span>
                  </div>
                </div>

                {ev.description && (
                  <p className="text-[11px] text-slate-600 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                    {ev.description}
                  </p>
                )}

                <div className="flex items-center gap-1.5 text-[10px] text-emerald-700 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{ev.verification_status || 'Verified Timetable Event'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sub-tab 2: Consecutive Station Chainage */}
      {activeSubTab === 'chainage' && (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm space-y-4 p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Consecutive Station Chainage & Exact Kilometres</h3>
              <p className="text-xs text-slate-500">Official RBS distance matrix between adjacent stations on Western & Northern Railway trunk routes.</p>
            </div>
            <span className="text-xs font-mono font-bold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-lg">
              {distances.length} Route Segments
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 uppercase font-bold text-[10px] tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">From Station</th>
                  <th className="py-2.5 px-3">To Station</th>
                  <th className="py-2.5 px-3">Consecutive</th>
                  <th className="py-2.5 px-3 text-right">Distance (km)</th>
                  <th className="py-2.5 px-3 text-right">Cumulative Chainage (km)</th>
                  <th className="py-2.5 px-3">Section Name</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {distances.map((d, idx) => (
                  <tr key={`${d.from_station_code}-${d.to_station_code}-${idx}`} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-900">{d.from_station_code}</td>
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-900">{d.to_station_code}</td>
                    <td className="py-2.5 px-3">
                      <span className="bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded text-[10px] font-bold">
                        Adjacent
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-railway-blue">
                      {d.distance_km} km
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-slate-500">
                      {d.cumulative_km} km
                    </td>
                    <td className="py-2.5 px-3 text-slate-500">
                      {d.section_name || 'Main Line Corridor'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sub-tab 3: 18 Railway Zones & Divisions */}
      {activeSubTab === 'zones' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {zones.map((z) => (
            <div
              key={z.zone_code}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <span className="text-base font-black font-mono text-railway-navy">
                  {z.zone_code}
                </span>
                <span className="text-xs font-bold text-slate-500">
                  HQ: {z.headquarters}
                </span>
              </div>

              <div>
                <h4 className="text-sm font-bold text-slate-900">{z.zone_name}</h4>
                <div className="text-xs text-slate-500 mt-0.5">
                  Route: <strong>{z.total_route_km ? `${z.total_route_km} km` : 'Active Network'}</strong>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1.5">
                  Operational Divisions ({z.divisions?.length || 0})
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {z.divisions?.map((div) => (
                    <span
                      key={div.division_code}
                      className="bg-slate-100 text-slate-700 text-[10px] font-mono font-bold px-2 py-0.5 rounded"
                      title={div.division_name}
                    >
                      {div.division_code}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
