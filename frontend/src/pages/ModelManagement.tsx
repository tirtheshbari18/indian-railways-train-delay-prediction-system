import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  Play, 
  CheckCircle2, 
  AlertCircle, 
  BarChart3, 
  Award, 
  ShieldCheck,
  Layers,
  ArrowRight
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend 
} from 'recharts';
import { api } from '../services/api';
import { ModelRegistryItem } from '../types';

export const ModelManagement: React.FC = () => {
  const [models, setModels] = useState<ModelRegistryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [training, setTraining] = useState<boolean>(false);
  const [activating, setActivating] = useState<string | null>(null);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const data = await api.getRegisteredModels();
      setModels(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    setTraining(true);
    setNotification(null);
    try {
      const res = await api.trainModels({ test_size: 0.2, auto_activate_best: true });
      setNotification({
        type: 'success',
        message: `Pipeline finished! Best model: ${res.best_model_name} (MAE: ${res.best_mae}m). Auto-promoted to live inference.`
      });
      loadModels();
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: err.response?.data?.detail || 'Training pipeline failed.'
      });
    } finally {
      setTraining(false);
    }
  };

  const handleActivate = async (modelName: string) => {
    setActivating(modelName);
    setNotification(null);
    try {
      await api.activateModel(modelName);
      setNotification({
        type: 'success',
        message: `Model ${modelName} is now active for live predictions.`
      });
      loadModels();
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to activate model.'
      });
    } finally {
      setActivating(null);
    }
  };

  // Chart data: compare MAE & RMSE
  const chartData = models.map(m => ({
    name: m.model_type,
    mae: m.mae,
    rmse: m.rmse,
    r2: m.r2_score,
    isActive: m.is_active,
  }));

  const activeModel = models.find(m => m.is_active) || models[0];

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs uppercase font-bold tracking-widest text-railway-blue">ML Registry & Operations</span>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Machine Learning Model Management</h2>
          <p className="text-sm text-slate-600">
            Compare candidate regression algorithms trained on strictly chronological splits. Active model powers live API predictions.
          </p>
        </div>

        <button
          onClick={handleRetrain}
          disabled={training}
          className="px-4 py-2.5 bg-railway-navy hover:bg-railway-blue text-white font-bold text-xs rounded-xl transition-all shadow-md flex items-center space-x-2 disabled:opacity-70"
        >
          {training ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Training 4 Models (Chronological Split)...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>Train All Models</span>
            </>
          )}
        </button>
      </div>

      {notification && (
        <div className={`p-4 rounded-xl text-xs flex items-center space-x-2 ${
          notification.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {notification.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
          )}
          <span>{notification.message}</span>
        </div>
      )}

      {/* Comparison Chart */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Unseen Test Set Performance (MAE & RMSE in Minutes)</h3>
            <p className="text-xs text-slate-500">Lower error reflects superior delay estimation precision</p>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-800 border border-blue-200">
            Chronological Split: 80% Train / 20% Test
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" fontSize={11} unit="m" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0B2545', color: '#fff', borderRadius: '8px', border: 'none' }}
                formatter={(val: any, name: any) => [`${val} minutes`, name === 'mae' ? 'MAE' : 'RMSE']}
              />
              <Legend verticalAlign="top" height={36} />
              <Bar dataKey="mae" name="Mean Absolute Error (MAE)" fill="#133E87" radius={[4, 4, 0, 0]} />
              <Bar dataKey="rmse" name="Root Mean Squared Error (RMSE)" fill="#F59E0B" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {models.map((m) => {
          const isActive = m.is_active;
          return (
            <div 
              key={m.id}
              className={`rounded-xl border p-5 transition-all shadow-sm flex flex-col justify-between ${
                isActive
                  ? 'bg-gradient-to-b from-blue-50/50 to-white border-blue-300 ring-2 ring-blue-500/20'
                  : 'bg-white border-slate-200 hover:border-slate-300'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
                    v{m.model_version}
                  </span>
                  {isActive && (
                    <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                      <ShieldCheck className="w-3 h-3 text-emerald-600" />
                      Active Live
                    </span>
                  )}
                </div>

                <h4 className="font-bold text-sm text-slate-900">{m.model_type}</h4>
                <div className="text-[11px] text-slate-500 font-mono mt-0.5 truncate">{m.model_name}</div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-slate-100 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px]">MAE (TEST)</span>
                    <span className="font-extrabold text-slate-900 text-sm">{m.mae}m</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">RMSE</span>
                    <span className="font-extrabold text-slate-900 text-sm">{m.rmse}m</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">R² SCORE</span>
                    <span className="font-bold text-emerald-700">{m.r2_score}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">TRAIN ROWS</span>
                    <span className="font-bold text-slate-700">{m.training_sample_count}</span>
                  </div>
                </div>
              </div>

              {/* Action */}
              <div className="mt-5 pt-3 border-t border-slate-100">
                {isActive ? (
                  <button
                    disabled
                    className="w-full py-1.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-lg text-xs font-bold cursor-default"
                  >
                    Currently In Service
                  </button>
                ) : (
                  <button
                    onClick={() => handleActivate(m.model_name)}
                    disabled={activating === m.model_name}
                    className="w-full py-1.5 bg-slate-100 hover:bg-railway-navy hover:text-white text-slate-700 rounded-lg text-xs font-semibold transition-all"
                  >
                    {activating === m.model_name ? 'Activating...' : 'Activate for Inference'}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Feature Engineering Columns Used */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
        <h3 className="text-sm font-bold text-slate-900">Features Ingested by Gradient Boosting Pipeline</h3>
        <div className="flex flex-wrap gap-2">
          {activeModel?.features_list.map((feat, idx) => (
            <span 
              key={idx}
              className="px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-xs font-mono font-medium text-slate-700"
            >
              {feat}
            </span>
          ))}
        </div>
      </div>

    </div>
  );
};
