import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  AlertTriangle, 
  MapPin, 
  Train, 
  TrendingUp, 
  Calendar,
  Info,
  ShieldCheck
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  ScatterChart, Scatter, ZAxis
} from 'recharts';
import { api } from '../services/api';
import { MostDelayedTrain, HighDelaySection, StationDelayItem, ActualVsPredictedItem } from '../types';

export const DelayAnalytics: React.FC = () => {
  const [mostDelayed, setMostDelayed] = useState<MostDelayedTrain[]>([]);
  const [sections, setSections] = useState<HighDelaySection[]>([]);
  const [stationDelays, setStationDelays] = useState<StationDelayItem[]>([]);
  const [actualVsPred, setActualVsPred] = useState<ActualVsPredictedItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const [delData, secData, stData, avpData] = await Promise.all([
        api.getMostDelayedTrains(15),
        api.getHighDelaySections(),
        api.getStationDelayFrequency(12),
        api.getActualVsPredicted(25),
      ]);
      setMostDelayed(delData);
      setSections(secData);
      setStationDelays(stData);
      setActualVsPred(avpData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-4 border-railway-blue border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Chart data for station delays
  const stationChartData = stationDelays.map(s => ({
    station: s.station_code,
    name: s.station_name,
    delay: s.avg_arrival_delay,
    recurringPct: s.recurring_delay_pct,
  }));

  // Chart data for actual vs predicted
  const avpChartData = actualVsPred.map(item => ({
    x: item.actual_delay,
    y: item.predicted_delay,
    train: item.train_number,
    station: item.station_code,
    error: item.error_minutes
  }));

  return (
    <div className="space-y-6">
      
      {/* Page Header */}
      <div>
        <span className="text-xs uppercase font-bold tracking-widest text-railway-blue">Network Intelligence</span>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Railway Delay & Bottleneck Analysis</h2>
        <p className="text-sm text-slate-600">
          In-depth empirical investigation of junction saturation, seasonal vulnerability, and schedule deviation patterns across Indian railway corridors.
        </p>
      </div>

      {/* Explanatory Scientific Caution Card */}
      <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 flex items-start space-x-3">
        <Info className="w-5 h-5 text-blue-700 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-blue-950">Analytical Methodology Note:</span>
          <p className="text-[11px] text-blue-800 mt-0.5 leading-relaxed">
            The insights surfaced below represent empirical statistical relationships observed across historical run logs. In complex rail systems, delays result from interconnected factors including signaling blocks, speed restrictions, and mixed traffic prioritization rather than isolated singular causes.
          </p>
        </div>
      </div>

      {/* Grid: Station Frequency Chart & Actual vs Predicted */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Station-wise Delay Frequency */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Station-wise Average Delay (Minutes)</h3>
            <p className="text-xs text-slate-500">Major transit hubs ranked by arrival delay minutes</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stationChartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="station" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} unit="m" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0B2545', color: '#fff', borderRadius: '8px', border: 'none' }}
                  formatter={(val: any) => [`${val}m`, 'Avg Delay']}
                  labelFormatter={(code, p) => `${p[0]?.payload?.name || code} (${code})`}
                />
                <Bar dataKey="delay" fill="#1E3E62" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Actual vs Predicted Delay Scatter */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Actual vs Predicted Delay Verification</h3>
            <p className="text-xs text-slate-500">Comparison of test arrivals: points along diagonal indicate strong agreement</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" dataKey="x" name="Actual Delay" unit="m" stroke="#94a3b8" fontSize={11} />
                <YAxis type="number" dataKey="y" name="Predicted Delay" unit="m" stroke="#94a3b8" fontSize={11} />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ payload }) => {
                    if (!payload || !payload.length) return null;
                    const d = payload[0].payload;
                    return (
                      <div className="bg-railway-navy text-white text-xs p-2.5 rounded-lg shadow-md border border-railway-steel">
                        <div className="font-bold">{d.train} @ {d.station}</div>
                        <div>Actual: {d.x}m</div>
                        <div>Predicted: {d.y}m</div>
                        <div className="text-amber-300">Residual Error: {d.error}m</div>
                      </div>
                    );
                  }}
                />
                <Scatter name="Arrivals" data={avpChartData} fill="#D97706" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Critical Railway Corridors Analysis */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">High-Friction Railway Corridors</h3>
          <p className="text-xs text-slate-500">
            Identified network sections exhibiting higher recurrence of delays, freight crossings, and weather disruptions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sections.map((sec, idx) => (
            <div 
              key={idx} 
              className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-white hover:border-slate-300 transition-all space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-200 text-slate-800">
                  {sec.zone} ZONE
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                  sec.risk_level === 'Critical' 
                    ? 'bg-red-100 text-red-800' 
                    : sec.risk_level === 'High' 
                    ? 'bg-orange-100 text-orange-800' 
                    : 'bg-amber-100 text-amber-800'
                }`}>
                  {sec.risk_level} Risk
                </span>
              </div>

              <div className="font-bold text-sm text-slate-900 mt-1">
                {sec.section_name}
              </div>

              <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-200/60">
                <span className="text-slate-500">Average Delay:</span>
                <span className="font-bold text-red-600">+{sec.average_delay_minutes} minutes</span>
              </div>

              <div className="text-[11px] text-slate-600 pt-1 leading-relaxed">
                <span className="font-semibold text-slate-700">Primary Dynamics:</span> {sec.primary_factor}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full Table: Most Delayed Trains */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Ranked Train Deviation Index</h3>
          <p className="text-xs text-slate-500">
            Train services sorted by highest historical schedule variance and late arrival percentage.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Train Number & Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4 text-right">Monitored Runs</th>
                <th className="py-3 px-4 text-right">Average Delay</th>
                <th className="py-3 px-4 text-right">Late Arrival Freq (%)</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {mostDelayed.map((tr) => (
                <tr key={tr.train_number} className="hover:bg-slate-50">
                  <td className="py-3 px-4">
                    <div className="font-bold text-slate-900">{tr.train_name}</div>
                    <div className="text-[11px] text-slate-500 font-mono">#{tr.train_number}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded bg-slate-100 font-semibold text-slate-700 text-[10px]">
                      {tr.train_category}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right text-slate-600 font-medium">
                    {tr.total_runs}
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-slate-900">
                    +{tr.average_delay_minutes}m
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className={`font-bold ${tr.delay_frequency_pct > 30 ? 'text-red-600' : 'text-amber-600'}`}>
                      {tr.delay_frequency_pct}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      tr.average_delay_minutes > 45 
                        ? 'bg-red-100 text-red-700' 
                        : tr.average_delay_minutes > 20 
                        ? 'bg-amber-100 text-amber-700' 
                        : 'bg-emerald-100 text-emerald-700'
                    }`}>
                      {tr.average_delay_minutes > 45 ? 'Severe Delays' : tr.average_delay_minutes > 20 ? 'Moderate Variance' : 'High Punctuality'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
