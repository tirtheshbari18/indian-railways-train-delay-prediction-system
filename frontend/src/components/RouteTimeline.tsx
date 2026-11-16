import React from 'react';
import { IntermediateStationPrediction } from '../types';
import { ArrowDown, TrendingUp, TrendingDown, Clock, MapPin } from 'lucide-react';

interface RouteTimelineProps {
  stations: IntermediateStationPrediction[];
  sourceStation: string;
  destStation: string;
}

export const RouteTimeline: React.FC<RouteTimelineProps> = ({
  stations,
  sourceStation,
  destStation
}) => {
  if (!stations || stations.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-300">
        No route data available to display.
      </div>
    );
  }

  const getDelayBadge = (delay: number) => {
    if (delay <= 15) {
      return {
        bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        dot: 'bg-emerald-500',
        label: delay <= 0 ? 'Right Time' : `+${delay}m`
      };
    } else if (delay <= 45) {
      return {
        bg: 'bg-amber-50 text-amber-700 border-amber-200',
        dot: 'bg-amber-500',
        label: `+${delay}m`
      };
    } else if (delay <= 120) {
      return {
        bg: 'bg-orange-50 text-orange-700 border-orange-200',
        dot: 'bg-orange-500',
        label: `+${delay}m`
      };
    } else {
      return {
        bg: 'bg-red-50 text-red-700 border-red-200',
        dot: 'bg-red-600',
        label: `+${delay}m Late`
      };
    }
  };

  return (
    <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200">
      {stations.map((st, idx) => {
        const isFirst = idx === 0;
        const isLast = idx === stations.length - 1;
        const badge = getDelayBadge(st.cumulative_delay_minutes);

        return (
          <div key={`${st.station_code}-${idx}`} className="relative group">
            {/* Timeline node icon */}
            <div
              className={`absolute -left-6 sm:-left-8 top-1 w-6 h-6 rounded-full flex items-center justify-center border-2 bg-white transition-all shadow-sm ${
                isFirst || isLast
                  ? 'border-railway-navy text-railway-navy'
                  : 'border-slate-300 text-slate-500'
              }`}
            >
              {isFirst || isLast ? (
                <MapPin className="w-3.5 h-3.5 fill-railway-navy text-white" />
              ) : (
                <div className={`w-2 h-2 rounded-full ${badge.dot}`} />
              )}
            </div>

            {/* Station Card */}
            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:border-slate-300 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                
                {/* Station Info */}
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-base font-bold text-slate-900">
                      {st.station_name}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs font-semibold">
                      {st.station_code}
                    </span>
                    {isFirst && (
                      <span className="text-[10px] bg-blue-100 text-blue-800 font-semibold px-2 py-0.5 rounded-full">
                        ORIGIN
                      </span>
                    )}
                    {isLast && (
                      <span className="text-[10px] bg-purple-100 text-purple-800 font-semibold px-2 py-0.5 rounded-full">
                        DESTINATION
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    Stop #{st.stop_number} • {st.distance_km} km from origin
                  </div>
                </div>

                {/* Timing & Delay Info */}
                <div className="flex items-center space-x-4">
                  {/* Scheduled vs Predicted */}
                  <div className="text-right">
                    <div className="text-xs text-slate-400 flex items-center justify-end gap-1">
                      <Clock className="w-3 h-3" />
                      <span>Sched: {st.scheduled_arrival || st.scheduled_departure || '--:--'}</span>
                    </div>
                    <div className="text-sm font-bold text-slate-800">
                      Expected: <span className="text-railway-blue">{st.predicted_arrival_time}</span>
                    </div>
                  </div>

                  {/* Delay Badge */}
                  <div className="text-right min-w-[90px]">
                    <span className={`inline-block px-2.5 py-1 rounded-md text-xs font-bold border ${badge.bg}`}>
                      {badge.label}
                    </span>
                    
                    {/* Compound or Recovery indicator */}
                    {!isFirst && (
                      <div className="text-[11px] mt-0.5 flex items-center justify-end font-medium">
                        {st.delay_change_minutes > 1.0 ? (
                          <span className="text-red-600 flex items-center">
                            <TrendingUp className="w-3 h-3 mr-0.5" /> +{st.delay_change_minutes}m
                          </span>
                        ) : st.delay_change_minutes < -1.0 ? (
                          <span className="text-emerald-600 flex items-center">
                            <TrendingDown className="w-3 h-3 mr-0.5" /> {st.delay_change_minutes}m
                          </span>
                        ) : (
                          <span className="text-slate-400">Steady</span>
                        )}
                      </div>
                    )}
                  </div>

                </div>

              </div>
            </div>

          </div>
        );
      })}
    </div>
  );
};
