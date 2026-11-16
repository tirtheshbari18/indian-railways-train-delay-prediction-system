import React, { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  RefreshCw, 
  Clock, 
  CheckCircle2, 
  AlertTriangle,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';
import { PredictionHistoryItem } from '../types';

export const PredictionHistory: React.FC = () => {
  const [history, setHistory] = useState<PredictionHistoryItem[]>([]);
  const [filterTrain, setFilterTrain] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getPredictionHistory(filterTrain || undefined, 50);
      setHistory(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadHistory();
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs uppercase font-bold tracking-widest text-railway-blue">Audit & Inference Archive</span>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Generated Delay Prediction Logs</h2>
          <p className="text-sm text-slate-600">
            Immutable log of all model inference requests, confidence intervals, and post-trip actual delay verification.
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex items-center space-x-2">
          <input
            type="text"
            placeholder="Filter by train number..."
            value={filterTrain}
            onChange={(e) => setFilterTrain(e.target.value)}
            className="px-3 py-1.5 text-xs bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-railway-blue font-mono"
          />
          <button
            type="submit"
            className="px-3 py-1.5 bg-railway-navy text-white rounded-lg text-xs font-semibold hover:bg-railway-blue transition-colors flex items-center gap-1"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Search</span>
          </button>
        </form>
      </div>

      {/* History Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Prediction ID</th>
                <th className="py-3 px-4">Train Service</th>
                <th className="py-3 px-4">Target Checkpoint</th>
                <th className="py-3 px-4">Journey Date</th>
                <th className="py-3 px-4 text-right">Predicted Delay</th>
                <th className="py-3 px-4">90% Confidence Interval</th>
                <th className="py-3 px-4 text-center">Late Probability</th>
                <th className="py-3 px-4 text-center">Category</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {Array.isArray(history) && history.length > 0 ? (
                history.map((h) => {
                  const delay = h.predicted_delay_minutes;
                  return (
                    <tr key={h.prediction_id} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-mono font-bold text-slate-700">
                        {h.prediction_id}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-900">{h.train_name}</div>
                        <div className="text-[11px] text-slate-500 font-mono">#{h.train_number} ({h.source_station} → {h.dest_station})</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded font-mono font-bold bg-blue-50 text-blue-800">
                          {h.target_station}
                        </span>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                          Sched: {h.scheduled_arrival} → Exp: {h.predicted_arrival_time}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-slate-600">
                        {h.journey_date}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span className="font-extrabold text-sm text-slate-900">
                          {delay > 0 ? `+${delay}` : delay}m
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-600">
                        [{h.confidence_interval.lower}m — {h.confidence_interval.upper}m]
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`font-bold ${h.late_probability > 0.5 ? 'text-red-600' : 'text-emerald-600'}`}>
                          {Math.round(h.late_probability * 100)}%
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          h.delay_category.includes('On-Time')
                            ? 'bg-emerald-100 text-emerald-800'
                            : h.delay_category.includes('Slight')
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {h.delay_category}
                        </span>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">
                    No prediction logs found. Make a prediction in the prediction portal to see entries here.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
