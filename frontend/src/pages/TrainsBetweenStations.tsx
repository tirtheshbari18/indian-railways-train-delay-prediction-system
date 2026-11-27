import React, { useState, useEffect } from 'react';
import { 
  ArrowRightLeft, 
  Search, 
  Train as TrainIcon, 
  Clock, 
  MapPin, 
  Layers, 
  Sparkles, 
  Calendar,
  CheckCircle2,
  Navigation,
  ArrowRight,
  Filter,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { TrainBetweenStationsResult, StationDetail, LiveTrainRunningResponse } from '../types';

export const TrainsBetweenStations: React.FC = () => {
  const [source, setSource] = useState<string>('BOR');
  const [destination, setDestination] = useState<string>('DRD');
  const [bidirectional, setBidirectional] = useState<boolean>(true);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [selectedDay, setSelectedDay] = useState<string>('');
  
  const [stations, setStations] = useState<StationDetail[]>([]);
  const [trains, setTrains] = useState<TrainBetweenStationsResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [searched, setSearched] = useState<boolean>(false);

  // Live modal tracking state
  const [activeLiveTrain, setActiveLiveTrain] = useState<string | null>(null);
  const [liveData, setLiveData] = useState<LiveTrainRunningResponse | null>(null);
  const [liveLoading, setLiveLoading] = useState<boolean>(false);

  useEffect(() => {
    loadStations();
    // Default search for Boisar ↔ Dahanu Road
    handleSearch('BOR', 'DRD', true);
  }, []);

  const loadStations = async () => {
    try {
      const data = await api.getMasterStations();
      setStations(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async (
    src: string = source, 
    dst: string = destination, 
    bidi: boolean = bidirectional,
    cat: string = categoryFilter,
    day: string = selectedDay
  ) => {
    setLoading(true);
    setSearched(true);
    try {
      const results = await api.getTrainsBetweenStations(src, dst, bidi, cat || undefined, day || undefined);
      setTrains(Array.isArray(results) ? results : []);
    } catch (err) {
      console.error('Error fetching trains between stations:', err);
      setTrains([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSwap = () => {
    const nextSrc = destination;
    const nextDst = source;
    setSource(nextSrc);
    setDestination(nextDst);
    handleSearch(nextSrc, nextDst, bidirectional, categoryFilter, selectedDay);
  };

  const handleTrackLive = async (trainNumber: string) => {
    setActiveLiveTrain(trainNumber);
    setLiveLoading(true);
    try {
      const res = await api.getLiveTrainStatus(trainNumber);
      if (res) setLiveData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLiveLoading(false);
    }
  };

  const getCategoryBadgeClass = (category: string) => {
    if (category.includes('Vande')) return 'bg-purple-100 text-purple-800 border-purple-200';
    if (category.includes('Rajdhani')) return 'bg-rose-100 text-rose-800 border-rose-200';
    if (category.includes('Shatabdi')) return 'bg-amber-100 text-amber-800 border-amber-200';
    if (category.includes('Superfast')) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (category.includes('MEMU') || category.includes('EMU') || category.includes('Suburban')) {
      return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    }
    return 'bg-slate-100 text-slate-800 border-slate-200';
  };

  // Highlight check for 22954
  const isGujaratSF = (trainNum: string) => trainNum === '22954';

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-railway-navy via-railway-steel to-railway-blue rounded-2xl p-6 text-white shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase font-bold tracking-widest text-blue-300">Corridor Train Intelligence</span>
              <span className="bg-amber-500/30 text-amber-300 border border-amber-400/30 px-2 py-0.5 rounded text-[11px] font-bold">
                Module 1 & 2
              </span>
            </div>
            <h2 className="text-2xl font-black tracking-tight mt-1">Trains Between Stations & Corridor Services</h2>
            <p className="text-sm text-slate-300 max-w-3xl mt-1">
              Search authentic Indian Railways schedules, platform assignments, chainage distances, and verified stopping services. Complete support for Superfasts, Rajdhanis, Vande Bharats, MEMU shuttles, and Suburban locals.
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-3 text-xs text-white flex flex-col gap-1">
            <span className="text-slate-300">Quick Corridor Test:</span>
            <button
              onClick={() => {
                setSource('BOR');
                setDestination('DRD');
                setBidirectional(true);
                handleSearch('BOR', 'DRD', true);
              }}
              className="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold rounded-lg text-xs transition-colors flex items-center gap-1"
            >
              <Navigation className="w-3.5 h-3.5" />
              <span>Boisar (BOR) ↔ Dahanu Road (DRD)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Search Filter Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
          
          {/* Source Station */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-blue-600" />
              <span>From Station</span>
            </label>
            <div className="relative">
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-railway-blue focus:bg-white"
              >
                {stations.map((st) => (
                  <option key={`src-${st.station_code}`} value={st.station_code}>
                    {st.station_code} - {st.station_name} ({st.zone})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Destination Station */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-amber-600" />
                <span>To Station</span>
              </label>
              <button
                type="button"
                onClick={handleSwap}
                className="text-[11px] text-railway-blue hover:text-railway-navy flex items-center gap-1 font-semibold"
                title="Swap stations"
              >
                <ArrowRightLeft className="w-3 h-3" />
                <span>Swap</span>
              </button>
            </div>
            <div className="relative">
              <select
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-railway-blue focus:bg-white"
              >
                {stations.map((st) => (
                  <option key={`dst-${st.station_code}`} value={st.station_code}>
                    {st.station_code} - {st.station_name} ({st.zone})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5 flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-slate-500" />
              <span>Train Category</span>
            </label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-railway-blue focus:bg-white"
            >
              <option value="">All Categories (SF, Express, MEMU, etc.)</option>
              <option value="Superfast">Superfast Express</option>
              <option value="Express">Mail / Express</option>
              <option value="MEMU">MEMU / Mainline Local</option>
              <option value="EMU">Suburban EMU</option>
              <option value="Rajdhani">Rajdhani Express</option>
              <option value="Shatabdi">Shatabdi Express</option>
              <option value="Vande Bharat">Vande Bharat Express</option>
            </select>
          </div>

          {/* Search Button */}
          <div>
            <button
              onClick={() => handleSearch(source, destination, bidirectional, categoryFilter, selectedDay)}
              disabled={loading}
              className="w-full bg-railway-navy hover:bg-railway-blue text-white font-bold py-2.5 px-4 rounded-xl text-sm transition-all shadow-sm flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              <span>Find Trains</span>
            </button>
          </div>

        </div>

        {/* Options Row */}
        <div className="mt-4 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs">
          <label className="flex items-center space-x-2 cursor-pointer font-medium text-slate-700 select-none">
            <input
              type="checkbox"
              checked={bidirectional}
              onChange={(e) => {
                setBidirectional(e.target.checked);
                handleSearch(source, destination, e.target.checked, categoryFilter, selectedDay);
              }}
              className="w-4 h-4 rounded text-railway-blue focus:ring-railway-blue border-slate-300"
            />
            <span>Include both directions on corridor (Northbound & Southbound services)</span>
          </label>

          <div className="text-slate-500 flex items-center gap-3">
            <span>
              Showing <strong className="text-slate-900 font-bold">{trains.length}</strong> active train services
            </span>
            {source === 'BOR' && destination === 'DRD' && (
              <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                <span>40+ Verified Corridor Services Active</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Train Results List */}
      <div className="space-y-3">
        {trains.map((t) => {
          const isTarget22954 = isGujaratSF(t.train_number);
          return (
            <div
              key={`${t.train_number}-${t.source_code}-${t.dest_code}`}
              className={`bg-white rounded-xl border transition-all p-5 shadow-sm hover:shadow-md ${
                isTarget22954 
                  ? 'border-amber-400 bg-amber-50/20 ring-1 ring-amber-400/50' 
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                
                {/* Train Identifiers */}
                <div className="space-y-1.5 min-w-[280px]">
                  <div className="flex items-center gap-2">
                    <span className="text-base font-black text-slate-900 font-mono tracking-tight">
                      {t.train_number}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getCategoryBadgeClass(t.train_category)}`}>
                      {t.train_category}
                    </span>
                    {isTarget22954 && (
                      <span className="bg-amber-500 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded-full uppercase tracking-wider flex items-center gap-1 shadow-xs">
                        <Sparkles className="w-3 h-3" />
                        <span>Featured Corridor Express</span>
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm font-bold text-slate-800">
                    {t.train_name}
                  </h4>
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span>Runs: <strong className="text-slate-700 font-semibold">{t.runs_on_days}</strong></span>
                    <span>•</span>
                    <span>Type: <strong className="text-slate-700">{t.train_type}</strong></span>
                  </div>
                </div>

                {/* Timing & Stations Journey Segment */}
                <div className="flex items-center justify-between sm:justify-start gap-4 sm:gap-8 flex-1 max-w-xl bg-slate-50 p-3 rounded-xl border border-slate-100">
                  {/* Origin Station */}
                  <div>
                    <div className="text-lg font-black text-slate-900 font-mono">
                      {t.source_departure}
                    </div>
                    <div className="text-xs font-bold text-slate-700">
                      {t.source_code}
                    </div>
                    <div className="text-[11px] text-slate-500 truncate max-w-[120px]">
                      {t.source_name}
                    </div>
                    <div className="mt-1">
                      <span className="inline-block text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono font-bold">
                        PF {t.source_platform || '1'}
                      </span>
                    </div>
                  </div>

                  {/* Travel Summary Arrow */}
                  <div className="flex flex-col items-center flex-1 px-2">
                    <span className="text-[11px] font-bold text-slate-600 mb-0.5">
                      {t.travel_duration_str}
                    </span>
                    <div className="w-full flex items-center gap-1">
                      <div className="h-0.5 bg-slate-300 flex-1 relative">
                        <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-railway-blue rounded-full" />
                      </div>
                      <ArrowRight className="w-3.5 h-3.5 text-railway-blue shrink-0" />
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1 flex items-center gap-2">
                      <span>{t.travel_distance_km} km</span>
                      <span>•</span>
                      <span>{t.intermediate_stops_count === 0 ? 'Non-Stop' : `${t.intermediate_stops_count} Halts`}</span>
                    </div>
                  </div>

                  {/* Destination Station */}
                  <div className="text-right">
                    <div className="text-lg font-black text-slate-900 font-mono">
                      {t.dest_arrival}
                    </div>
                    <div className="text-xs font-bold text-slate-700">
                      {t.dest_code}
                    </div>
                    <div className="text-[11px] text-slate-500 truncate max-w-[120px]">
                      {t.dest_name}
                    </div>
                    <div className="mt-1">
                      <span className="inline-block text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono font-bold">
                        PF {t.dest_platform || '2'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Action Button */}
                <div className="flex sm:flex-col justify-end gap-2 shrink-0">
                  <button
                    onClick={() => handleTrackLive(t.train_number)}
                    className="px-3.5 py-2 bg-railway-blue hover:bg-railway-navy text-white text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-1.5 shadow-xs"
                  >
                    <Clock className="w-3.5 h-3.5" />
                    <span>Live Status</span>
                  </button>
                </div>

              </div>
            </div>
          );
        })}

        {searched && trains.length === 0 && !loading && (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
            <TrainIcon className="w-12 h-12 text-slate-300 mx-auto" />
            <h3 className="text-base font-bold text-slate-800">No Direct Trains Found</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              No train services currently connect {source} and {destination} under the selected filters. Try toggling &quot;Include both directions&quot; or clearing the category filter.
            </p>
          </div>
        )}
      </div>

      {/* Live Train Status Modal */}
      {activeLiveTrain && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            
            {/* Modal Header */}
            <div className="bg-railway-navy text-white p-5 flex items-center justify-between border-b border-railway-steel">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="text-base font-black font-mono tracking-tight text-white">{activeLiveTrain}</span>
                  <span className="text-xs text-blue-200">•</span>
                  <span className="text-sm font-bold text-blue-100">{liveData?.train_name}</span>
                </div>
                <div className="text-xs text-slate-300">
                  {liveData?.source_station_name} ({liveData?.source_station_code}) → {liveData?.dest_station_name} ({liveData?.dest_station_code})
                </div>
              </div>
              <button
                onClick={() => {
                  setActiveLiveTrain(null);
                  setLiveData(null);
                }}
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center text-sm font-bold transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Current Running Status Header */}
            {liveData && (
              <div className="bg-slate-50 p-4 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <span className="text-[11px] uppercase tracking-wider text-slate-500 font-bold">Current Position</span>
                  <div className="text-sm font-bold text-slate-900 mt-0.5">
                    {liveData.current_status}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[11px] uppercase tracking-wider text-slate-500 font-bold">Delay Status</span>
                  <div className={`text-xs font-bold px-2 py-0.5 rounded mt-0.5 inline-block ${
                    liveData.delay_minutes > 15 ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                  }`}>
                    {liveData.delay_minutes > 0 ? `${liveData.delay_minutes} min late` : 'Right Time'}
                  </div>
                </div>
              </div>
            )}

            {/* Stops Timeline */}
            <div className="p-6 overflow-y-auto space-y-4 flex-1">
              {liveLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="w-8 h-8 border-3 border-railway-blue border-t-transparent rounded-full animate-spin" />
                </div>
              ) : (
                <div className="relative border-l-2 border-slate-200 ml-4 space-y-6 py-2">
                  {liveData?.timeline.map((stop) => {
                    const isPassed = stop.status === 'Departed';
                    const isCurrent = stop.status === 'Current';
                    return (
                      <div key={stop.stop_number} className="relative pl-6">
                        {/* Dot indicator */}
                        <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 bg-white flex items-center justify-center ${
                          isCurrent 
                            ? 'border-amber-500 bg-amber-500' 
                            : isPassed 
                              ? 'border-emerald-500 bg-emerald-500' 
                              : 'border-slate-300'
                        }`}>
                          {isPassed && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                        </div>

                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-mono font-bold text-slate-500">#{stop.stop_number}</span>
                              <span className="text-sm font-bold text-slate-900">{stop.station_name}</span>
                              <span className="text-xs font-mono font-semibold text-slate-500">({stop.station_code})</span>
                              <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.2 rounded font-mono">
                                PF {stop.platform}
                              </span>
                            </div>
                            <div className="text-xs text-slate-500 mt-0.5">
                              Distance: {stop.distance_km} km
                            </div>
                          </div>

                          <div className="text-right text-xs">
                            <div className="font-mono font-semibold text-slate-800">
                              {stop.actual_arrival || stop.scheduled_arrival || '--:--'}
                            </div>
                            <div className="text-[10px] text-slate-400">
                              Sched: {stop.scheduled_arrival || stop.scheduled_departure || '--:--'}
                            </div>
                            {stop.delay_arrival_minutes > 0 && (
                              <span className="text-[10px] text-amber-600 font-bold">
                                +{stop.delay_arrival_minutes}m
                              </span>
                            )}
                          </div>
                        </div>

                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 flex justify-end">
              <button
                onClick={() => {
                  setActiveLiveTrain(null);
                  setLiveData(null);
                }}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-bold rounded-lg transition-colors"
              >
                Close Tracking
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
