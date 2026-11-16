import React from 'react';
import { Train, Activity, Cpu, ShieldCheck } from 'lucide-react';

interface NavbarProps {
  activeModelName?: string;
  onTimePct?: number;
}

export const Navbar: React.FC<NavbarProps> = ({ activeModelName = 'XGBoost Regressor (v1.0)', onTimePct = 78.5 }) => {
  return (
    <header className="bg-railway-navy text-white border-b border-railway-steel/50 shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Railway Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-railway-blue to-railway-navy flex items-center justify-center border border-blue-400/30 shadow-inner">
              <Train className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs uppercase tracking-wider font-semibold text-blue-200">भारतीय रेल | Indian Railways</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-400/30">AI PLATFORM</span>
              </div>
              <h1 className="text-base sm:text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                Train Delay Prediction & Punctuality Analytics
              </h1>
            </div>
          </div>

          {/* Quick System Badges */}
          <div className="hidden md:flex items-center space-x-4 text-xs">
            <div className="flex items-center space-x-1.5 bg-railway-steel/60 px-3 py-1.5 rounded-md border border-railway-steel">
              <Cpu className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-300">Active Model:</span>
              <span className="font-semibold text-white">{activeModelName}</span>
            </div>

            <div className="flex items-center space-x-1.5 bg-railway-steel/60 px-3 py-1.5 rounded-md border border-railway-steel">
              <Activity className="w-4 h-4 text-blue-400" />
              <span className="text-slate-300">Network Punctuality:</span>
              <span className="font-bold text-emerald-300">{onTimePct}%</span>
            </div>

            <div className="flex items-center space-x-1 text-slate-300 bg-emerald-950/40 border border-emerald-500/30 px-2.5 py-1.5 rounded-md">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[11px] font-medium text-emerald-300">Operational ML Live</span>
            </div>
          </div>

        </div>
      </div>
    </header>
  );
};
