import React from 'react';
import { 
  LayoutDashboard, 
  Clock, 
  GitCommit, 
  BarChart3, 
  Database, 
  Cpu, 
  History,
  FileSpreadsheet
} from 'lucide-react';

export type NavTab = 'dashboard' | 'predict' | 'route' | 'analytics' | 'datasets' | 'models' | 'history';

interface SidebarProps {
  currentTab: NavTab;
  onTabChange: (tab: NavTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange }) => {
  const navItems = [
    { id: 'dashboard' as NavTab, label: 'Analytics Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'predict' as NavTab, label: 'Train Delay Prediction', icon: Clock, badge: 'AI ML' },
    { id: 'route' as NavTab, label: 'Route & Intermediate Stops', icon: GitCommit, badge: 'Dynamic' },
    { id: 'analytics' as NavTab, label: 'Railway Delay Analytics', icon: BarChart3, badge: null },
    { id: 'datasets' as NavTab, label: 'Historical Datasets', icon: Database, badge: null },
    { id: 'models' as NavTab, label: 'Model Management', icon: Cpu, badge: 'Admin' },
    { id: 'history' as NavTab, label: 'Prediction Logs', icon: History, badge: null },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 shadow-sm">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Operations & Intelligence
        </div>
        
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-railway-navy text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-300' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-600 border border-slate-200'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Railway Information footer card */}
      <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 mt-6 text-xs text-slate-500 space-y-1">
        <div className="font-semibold text-slate-800 flex items-center gap-1.5">
          <FileSpreadsheet className="w-4 h-4 text-railway-blue" />
          <span>Operational Benchmark</span>
        </div>
        <p className="text-[11px] text-slate-600 leading-relaxed">
          Trained on chronological Indian Railways timetables, delay records, and fog corridor weather indices.
        </p>
      </div>
    </aside>
  );
};
