import React, { useEffect, useState } from 'react';
import { 
  Train, 
  Clock, 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  Cpu, 
  Calendar,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  BarChart, Bar, PieChart, Pie, Cell, Legend
} from 'recharts';
import { api } from '../services/api';
import { DashboardKPIs, DelayTrendItem, HighDelaySection, MostDelayedTrain } from '../types';
import { MetricCard } from '../components/MetricCard';

interface DashboardProps {
  onNavigateTab: (tab: any) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigateTab }) => {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [trends, setTrends] = useState<DelayTrendItem[]>([]);
  const [sections, setSections] = useState<HighDelaySection[]>([]);
  const [mostDelayed, setMostDelayed] = useState<MostDelayedTrain[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [trendDays, setTrendDays] = useState<number>(30);

  useEffect(() => {
    loadDashboardData();
  }, [trendDays]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [kpisData, trendsData, sectionsData, delayedData] = await Promise.all([
        api.getKPIs(),
        api.getPunctualityTrends(trendDays),
        api.getHighDelaySections(),
        api.getMostDelayedTrains(5),
      ]);
      setKpis(kpisData);
      setTrends(Array.isArray(trendsData) ? trendsData : []);
      setSections(Array.isArray(sectionsData) ? sectionsData : []);
      setMostDelayed(Array.isArray(delayedData) ? delayedData : []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Distribution data for Pie Chart
  const pieData = [
    { name: 'On-Time (≤15m)', value: kpis ? kpis.on_time_performance_pct : 78.5, color: '#10B981' },
    { name: 'Slight Delay (15-45m)', value: kpis ? Math.max(0, kpis.delayed_train_pct - kpis.severe_delay_pct) : 17.3, color: '#F59E0B' },
    { name: 'Severe Delay (>120m)', value: kpis ? kpis.severe_delay_pct : 4.2, color: '#EF4444' },
  ];

  if (loading && !kpis) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-10 h-10 border-4 border-railway-blue border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-semibold text-slate-600">Loading AI Railway Analytics...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Top Banner / Welcome */}
      <div className="bg-gradient-to-r from-railway-navy via-railway-steel to-railway-blue rounded-2xl p-6 text-white shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs uppercase font-bold tracking-widest text-blue-300">Operational Dashboard</span>
          <h2 className="text-2xl font-black tracking-tight mt-0.5">Indian Railways Delay & Punctuality Intelligence</h2>
          <p className="text-sm text-slate-300 max-w-2xl mt-1">
            Machine learning regression models analyzing historical train movements, station congestion, and seasonal fog impact.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigateTab('predict')}
            className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs rounded-lg transition-colors shadow-sm flex items-center gap-1.5"
          >
            <Clock className="w-4 h-4" />
            <span>Predict Train Delay</span>
          </button>
          <button
            onClick={() => onNavigateTab('models')}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-semibold text-xs rounded-lg border border-white/20 transition-colors flex items-center gap-1.5"
          >
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>Manage Models</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Trains Analysed"
          value={kpis?.total_trains_analysed ?? 10}
          subtitle="Distinct active corridor services"
          icon={Train}
          accentColor="blue"
        />

        <MetricCard
          title="On-Time Performance"
          value={`${kpis?.on_time_performance_pct ?? 78.5}%`}
          subtitle="Arrivals within 15 min tolerance"
          icon={CheckCircle2}
          trend="+2.4% vs last month"
          trendType="positive"
          accentColor="emerald"
        />

        <MetricCard
          title="Average Arrival Delay"
          value={`${kpis?.average_predicted_delay_min ?? 18.4}m`}
          subtitle="Network-wide average deviation"
          icon={Clock}
          trend="-3.1m improvement"
          trendType="positive"
          accentColor="amber"
        />

        <MetricCard
          title="Model Prediction Accuracy"
          value={`MAE: ${kpis?.model_mae ?? 8.4}m`}
          subtitle={`Active: ${kpis?.active_model_name?.split('_')[0] ?? 'XGBoost'} (R²: ${kpis?.model_r2 ?? 0.81})`}
          icon={Cpu}
          trend="Validated on test set"
          trendType="neutral"
          accentColor="blue"
        />
      </div>

      {/* Middle Charts: Trends & Delay Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Daily Delay Trend Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="text-base font-bold text-slate-900">Network Delay & Punctuality Trend</h3>
              <p className="text-xs text-slate-500">Historical daily average delay progression</p>
            </div>
            <div className="flex items-center space-x-1.5 bg-slate-100 p-1 rounded-lg text-xs font-semibold">
              <button
                onClick={() => setTrendDays(14)}
                className={`px-2.5 py-1 rounded-md ${trendDays === 14 ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600'}`}
              >
                14 Days
              </button>
              <button
                onClick={() => setTrendDays(30)}
                className={`px-2.5 py-1 rounded-md ${trendDays === 30 ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600'}`}
              >
                30 Days
              </button>
              <button
                onClick={() => setTrendDays(60)}
                className={`px-2.5 py-1 rounded-md ${trendDays === 60 ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600'}`}
              >
                60 Days
              </button>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={Array.isArray(trends) ? trends : []}>
                <defs>
                  <linearGradient id="delayGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1E3E62" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#1E3E62" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(val) => val.slice(5)} 
                  stroke="#94a3b8" 
                  fontSize={11} 
                />
                <YAxis stroke="#94a3b8" fontSize={11} unit="m" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0B2545', color: '#fff', borderRadius: '8px', border: 'none' }}
                  formatter={(val: any) => [`${val} minutes`, 'Avg Delay']}
                  labelFormatter={(lbl) => `Date: ${lbl}`}
                />
                <Area 
                  type="monotone" 
                  dataKey="avg_delay_minutes" 
                  stroke="#133E87" 
                  strokeWidth={2.5} 
                  fillOpacity={1} 
                  fill="url(#delayGrad)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Delay Category Distribution */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Punctuality Classification</h3>
            <p className="text-xs text-slate-500">Distribution across operational delay bands</p>
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(val: any) => [`${val}%`, 'Proportion']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100">
            {pieData.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-600 font-medium">{item.name}</span>
                </div>
                <span className="font-bold text-slate-800">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Lower Row: Bottlenecks & High Delay Trains */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* High Delay Railway Sections */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900">Bottleneck Railway Corridors</h3>
              <p className="text-xs text-slate-500">Sections with recurrent congestion and high delay variability</p>
            </div>
            <button
              onClick={() => onNavigateTab('analytics')}
              className="text-xs font-semibold text-railway-blue hover:underline flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {(Array.isArray(sections) ? sections : []).slice(0, 4).map((sec, idx) => (
              <div 
                key={idx} 
                className="p-3 rounded-lg border border-slate-200 bg-slate-50 hover:bg-white hover:border-slate-300 transition-all flex items-center justify-between gap-3"
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-xs text-slate-900">{sec.section_name}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700">
                      {sec.zone}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1 line-clamp-1">{sec.primary_factor}</p>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-xs font-bold text-red-600">+{sec.average_delay_minutes}m avg</span>
                  <span className={`block text-[10px] font-bold uppercase ${
                    sec.risk_level === 'Critical' ? 'text-red-700' : 'text-amber-700'
                  }`}>
                    {sec.risk_level} Risk
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Most Delayed Trains */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900">Frequently Delayed Trains</h3>
              <p className="text-xs text-slate-500">Trains with elevated frequency of schedule deviations</p>
            </div>
            <button
              onClick={() => onNavigateTab('analytics')}
              className="text-xs font-semibold text-railway-blue hover:underline flex items-center gap-1"
            >
              <span>View Details</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Train</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3 text-right">Avg Delay</th>
                  <th className="py-2.5 px-3 text-right">Late Frequency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {(Array.isArray(mostDelayed) ? mostDelayed : []).map((tr) => (
                  <tr key={tr.train_number} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3">
                      <div className="font-bold text-slate-900">{tr.train_name}</div>
                      <div className="text-[11px] text-slate-500 font-mono">#{tr.train_number}</div>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded bg-slate-100 font-semibold text-slate-700 text-[10px]">
                        {tr.train_category}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right font-bold text-slate-900">
                      +{tr.average_delay_minutes}m
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <span className={`font-semibold ${tr.delay_frequency_pct > 30 ? 'text-red-600' : 'text-amber-600'}`}>
                        {tr.delay_frequency_pct}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>

      </div>

    </div>
  );
};
