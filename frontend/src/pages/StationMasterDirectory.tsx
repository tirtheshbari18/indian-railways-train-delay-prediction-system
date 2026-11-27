import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Search, 
  Filter, 
  MapPin, 
  Layers, 
  CheckCircle2, 
  Zap, 
  Maximize2,
  Train,
  ArrowUpDown
} from 'lucide-react';
import { api } from '../services/api';
import { StationDetail, StationPlatform } from '../types';

export const StationMasterDirectory: React.FC = () => {
  const [stations, setStations] = useState<StationDetail[]>([]);
  const [search, setSearch] = useState<string>('');
  const [selectedZone, setSelectedZone] = useState<string>('');
  const [selectedStation, setSelectedStation] = useState<StationDetail | null>(null);
  const [platforms, setPlatforms] = useState<StationPlatform[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadStations();
  }, [search, selectedZone]);

  const loadStations = async () => {
    setLoading(true);
    try {
      const data = await api.getMasterStations(search || undefined, selectedZone || undefined);
      setStations(Array.isArray(data) ? data : []);
      if (!selectedStation && data && data.length > 0) {
        // Default to Boisar or first
        const defaultSt = data.find((s: StationDetail) => s.station_code === 'BOR') || data[0];
        handleSelectStation(defaultSt);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectStation = async (st: StationDetail) => {
    setSelectedStation(st);
    try {
      const pfs = await api.getStationPlatforms(st.station_code);
      setPlatforms(Array.isArray(pfs) ? pfs : (st.platforms || []));
    } catch {
      setPlatforms(st.platforms || []);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-railway-navy via-railway-steel to-railway-blue rounded-2xl p-6 text-white shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase font-bold tracking-widest text-blue-300">Station Infrastructure</span>
            <span className="bg-amber-500/30 text-amber-300 border border-amber-400/30 px-2 py-0.5 rounded text-[11px] font-bold">
              Module 3 & 6
            </span>
          </div>
          <h2 className="text-2xl font-black tracking-tight mt-1">Station Master Database & Verified Platform Count</h2>
          <p className="text-sm text-slate-300 max-w-2xl mt-1">
            Complete registry of Indian Railways stations with physical platform counts, platform lengths, Island vs Side configurations, electrification, and operational divisions.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-xl border border-white/20 text-xs">
          <span>Active Master Registry:</span>
          <strong className="text-white font-bold">{stations.length} Stations</strong>
        </div>
      </div>

      {/* Filter Row */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        
        <div className="relative flex-1 w-full sm:max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by station code (e.g. BOR, DRD, MMCT) or city name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-9 pr-4 py-2 text-xs font-semibold text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-railway-blue focus:bg-white"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-railway-blue"
          >
            <option value="">All Zones</option>
            <option value="WR">Western Railway (WR)</option>
            <option value="CR">Central Railway (CR)</option>
            <option value="NR">Northern Railway (NR)</option>
            <option value="NCR">North Central Railway (NCR)</option>
            <option value="WCR">West Central Railway (WCR)</option>
          </select>
        </div>

      </div>

      {/* Main Grid: Station List + Platform Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left: Station Cards List */}
        <div className="space-y-3 max-h-[680px] overflow-y-auto pr-1">
          {stations.map((st) => {
            const isSelected = selectedStation?.station_code === st.station_code;
            return (
              <div
                key={st.station_code}
                onClick={() => handleSelectStation(st)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? 'border-railway-blue bg-blue-50/40 shadow-sm ring-1 ring-railway-blue'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-black text-slate-900 font-mono">{st.station_code}</span>
                      <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded">
                        {st.zone} / {st.division}
                      </span>
                    </div>
                    <h4 className="text-xs font-bold text-slate-800 mt-1">{st.station_name}</h4>
                    <div className="text-[11px] text-slate-500 mt-0.5">{st.city}, {st.state}</div>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-black text-railway-navy bg-white border border-slate-200 px-2 py-1 rounded-lg shadow-2xs block">
                      {st.total_platforms} Platforms
                    </span>
                    <span className="text-[10px] text-slate-400 mt-1 block">
                      {st.station_category || 'NSG-2'}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Selected Station Platform Inspector */}
        <div className="lg:col-span-2 space-y-5">
          {selectedStation ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
              
              {/* Header Info */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-5">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xl font-black font-mono text-slate-900">{selectedStation.station_code}</span>
                    <span className="text-xs font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                      {selectedStation.zone} • {selectedStation.division} Division
                    </span>
                    <span className="text-xs font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded">
                      Category: {selectedStation.station_category || 'NSG-2'}
                    </span>
                  </div>
                  <h3 className="text-xl font-black text-slate-900 mt-1">{selectedStation.station_name}</h3>
                  {selectedStation.alternative_names && selectedStation.alternative_names.length > 0 && (
                    <div className="text-xs text-slate-500 mt-0.5">
                      Also known as: <span className="font-semibold text-slate-700">{selectedStation.alternative_names.join(', ')}</span>
                    </div>
                  )}
                </div>

                <div className="text-right sm:border-l sm:border-slate-100 sm:pl-5">
                  <div className="text-xs text-slate-500 font-semibold">Total Verified Platforms</div>
                  <div className="text-3xl font-black text-railway-blue mt-0.5">
                    {selectedStation.total_platforms}
                  </div>
                  <div className="text-[11px] text-slate-400">All Berthing Tracks Verified</div>
                </div>
              </div>

              {/* Station Parameters Overview */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Railway Lines</span>
                  <span className="text-sm font-black text-slate-800 mt-0.5 block">{selectedStation.lines_count || 4} Tracks</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Track Gauge</span>
                  <span className="text-sm font-black text-slate-800 mt-0.5 block">1676 mm (Broad)</span>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Electrification</span>
                  <span className="text-sm font-black text-emerald-600 mt-0.5 flex items-center gap-1">
                    <Zap className="w-3.5 h-3.5" />
                    <span>25 kV AC</span>
                  </span>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Elevation</span>
                  <span className="text-sm font-black text-slate-800 mt-0.5 block">{selectedStation.elevation || 15} m MSL</span>
                </div>
              </div>

              {/* Station Platforms Grid */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                    <Layers className="w-4 h-4 text-railway-blue" />
                    <span>Station Platform Architecture & Line Layout</span>
                  </h4>
                  <span className="text-xs text-slate-500">
                    Showing all {platforms.length} platforms
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {platforms.map((pf) => (
                    <div
                      key={pf.platform_number}
                      className="border border-slate-200 rounded-xl p-3.5 bg-slate-50/50 hover:bg-white transition-colors space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="w-7 h-7 rounded-lg bg-railway-navy text-white font-mono font-black text-xs flex items-center justify-center">
                            {pf.platform_number}
                          </span>
                          <span className="text-xs font-bold text-slate-800">
                            Platform {pf.platform_number}
                          </span>
                        </div>
                        <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                          {pf.status || 'Operational'}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-600 pt-1 border-t border-slate-100">
                        <div>
                          <span className="text-slate-400 block text-[10px]">Type:</span>
                          <strong className="text-slate-700">{pf.platform_type}</strong>
                        </div>
                        <div>
                          <span className="text-slate-400 block text-[10px]">Length:</span>
                          <strong className="text-slate-700">{pf.platform_length_m || 600} metres (24-Coach)</strong>
                        </div>
                      </div>

                      <div className="text-[10px] text-slate-500 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        <span>Electrified Overhead Catenary • Line {pf.platform_number}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400">
              Select a station from the list to view its verified platform count and layout.
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
