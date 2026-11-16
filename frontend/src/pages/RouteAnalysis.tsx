import React, { useState, useEffect } from 'react';
import { 
  GitCommit, 
  Play, 
  AlertTriangle, 
  CheckCircle2, 
  MapPin, 
  TrendingUp,
  TrendingDown,
  Layers,
  ArrowRight
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid 
} from 'recharts';
import { api } from '../services/api';
import { Train, RoutePredictionResponse } from '../types';
import { RouteTimeline } from '../components/RouteTimeline';

export const RouteAnalysis: React.FC = () => {
  const [trains, setTrains] = useState<Train[]>([]);
  const [selectedTrainNum, setSelectedTrainNum] = useState<string>('12951');
  const [journeyDate, setJourneyDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [initialDelay, setInitialDelay] = useState<number>(0);
  const [weatherCondition, setWeatherCondition] = useState<string>('Clear');

  const [routeResult, setRouteResult] = useState<RoutePredictionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    loadTrains();
  }, []);

  const loadTrains = async () => {
    try {
      const data = await api.getTrains();
      const safeData = Array.isArray(data) ? data : [];
      setTrains(safeData);
      if (safeData.length > 0) {
        setSelectedTrainNum(safeData[0].train_number);
        fetchRoutePredictions(safeData[0].train_number, 0, 'Clear');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchRoutePredictions = async (trainNum: string, initDelay: number, weather: string) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.predictRouteDelays({
        train_number: trainNum,
        journey_date: journeyDate,
        initial_delay_minutes: Number(initDelay),
        weather_condition: weather
      });
      setRouteResult(res);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to simulate route delays.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRoutePredictions(selectedTrainNum, initialDelay, weatherCondition);
  };

  // Chart data: Station Name vs Cumulative Delay
  const chartData = (Array.isArray(routeResult?.intermediate_stations) ? routeResult.intermediate_stations : []).map(st => ({
    name: st.station_code,
    fullName: st.station_name,
    delay: st.cumulative_delay_minutes,
    distance: st.distance_km,
  }));

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div>
        <span className="text-xs uppercase font-bold tracking-widest text-railway-blue">Route Progression Engine</span>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Intermediate Station Delay Analysis</h2>
        <p className="text-sm text-slate-600">
          Dynamic route propagation model tracking compounding delays, track congestion bottlenecks, and schedule buffer recovery across all stops.
        </p>
      </div>

      {/* Control Bar Form */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
          
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
              Select Train Service
            </label>
            <select
              value={selectedTrainNum}
              onChange={(e) => setSelectedTrainNum(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-railway-blue"
            >
              {(Array.isArray(trains) ? trains : []).map((t) => (
                <option key={t.train_number} value={t.train_number}>
                  {t.train_number} - {t.train_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Journey Date</label>
            <input
              type="date"
              value={journeyDate}
              onChange={(e) => setJourneyDate(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Initial Departure Delay (m)</label>
            <input
              type="number"
              min="0"
              max="300"
              value={initialDelay}
              onChange={(e) => setInitialDelay(Number(e.target.value))}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Corridor Weather</label>
            <select
              value={weatherCondition}
              onChange={(e) => setWeatherCondition(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
            >
              <option value="Clear">Clear Skies</option>
              <option value="Rain">Monsoon Rain</option>
              <option value="Fog">Winter Fog (NCR Corridor)</option>
              <option value="Dense Fog">Dense Fog (Severe Speed Reduction)</option>
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-railway-navy hover:bg-railway-blue text-white font-bold text-xs rounded-lg transition-all shadow-sm flex items-center justify-center space-x-1.5 disabled:opacity-70"
            >
              {loading ? (
                <span>Simulating...</span>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-white" />
                  <span>Simulate Route Delays</span>
                </>
              )}
            </button>
          </div>

        </form>
      </div>

      {errorMsg && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl">
          {errorMsg}
        </div>
      )}

      {routeResult && (
        <div className="space-y-6">
          
          {/* Summary Strip */}
          <div className="bg-gradient-to-r from-railway-navy to-railway-steel text-white rounded-xl p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-blue-200">
                {routeResult.train_number} • {routeResult.train_name}
              </span>
              <div className="text-xl font-black mt-0.5 flex items-center gap-2">
                <span>{routeResult.source_station}</span>
                <ArrowRight className="w-4 h-4 text-slate-300" />
                <span>{routeResult.destination_station}</span>
                <span className="text-xs font-normal text-slate-300">({routeResult.total_distance_km} km)</span>
              </div>
            </div>

            <div className="flex items-center space-x-6 text-right">
              <div>
                <span className="text-xs text-slate-300 block">Scheduled Final Arrival</span>
                <span className="text-lg font-bold text-slate-100">{routeResult.final_scheduled_arrival}</span>
              </div>
              <div className="border-l border-white/20 pl-6">
                <span className="text-xs text-slate-300 block">AI Predicted Arrival</span>
                <span className="text-xl font-extrabold text-amber-300">{routeResult.final_predicted_arrival}</span>
                <span className="text-xs text-amber-200 block">
                  (+{routeResult.final_predicted_delay_minutes}m final delay)
                </span>
              </div>
            </div>
          </div>

          {/* Delay Evolution Graph across Stations */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Cumulative Delay Trajectory Along Route</h3>
              <p className="text-xs text-slate-500">
                Notice how delay compounds in congested junctions and can recover during buffer stretches.
              </p>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} unit="m" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0B2545', color: '#fff', borderRadius: '8px', border: 'none' }}
                    formatter={(val: any) => [`${val} minutes`, 'Delay']}
                    labelFormatter={(code, p) => {
                      const item = p[0]?.payload;
                      return `${item?.fullName || code} (${code}) • ${item?.distance} km`;
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="delay" 
                    stroke="#D97706" 
                    strokeWidth={3} 
                    dot={{ fill: '#0B2545', r: 5 }} 
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Bottlenecks and Recovery Lists */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* High-risk segments */}
            <div className="bg-red-50/60 border border-red-200 rounded-xl p-4 space-y-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-red-800 uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <span>Identified Bottleneck Segments</span>
              </div>
              <ul className="space-y-1.5 text-xs text-red-700">
                {(Array.isArray(routeResult.high_risk_segments) ? routeResult.high_risk_segments : []).map((s, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="font-bold">•</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Recovery opportunities */}
            <div className="bg-emerald-50/60 border border-emerald-200 rounded-xl p-4 space-y-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-emerald-800 uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Schedule Slack Recovery Windows</span>
              </div>
              <ul className="space-y-1.5 text-xs text-emerald-700">
                {(Array.isArray(routeResult.recovery_opportunities) ? routeResult.recovery_opportunities : []).map((o, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="font-bold">•</span>
                    <span>{o}</span>
                  </li>
                ))}
              </ul>
            </div>

          </div>

          {/* Detailed Intermediate Stations Timeline */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Station-by-Station Timetable & Predicted Arrival</h3>
              <p className="text-xs text-slate-500">
                Chronological breakdown of scheduled vs expected arrival, halt duration, and compounding delays.
              </p>
            </div>

            <RouteTimeline
              stations={routeResult.intermediate_stations}
              sourceStation={routeResult.source_station}
              destStation={routeResult.destination_station}
            />
          </div>

        </div>
      )}

    </div>
  );
};
