import React from 'react';

interface DelayGaugeProps {
  lateProbability: number; // 0.0 to 1.0
  predictedDelay: number;
  confidenceLower: number;
  confidenceUpper: number;
  delayCategory: string;
}

export const DelayGauge: React.FC<DelayGaugeProps> = ({
  lateProbability,
  predictedDelay,
  confidenceLower,
  confidenceUpper,
  delayCategory
}) => {
  const latePercent = Math.round(lateProbability * 100);
  const onTimePercent = 100 - latePercent;

  const getCategoryTheme = (cat: string) => {
    if (cat.includes('On-Time')) {
      return {
        badgeBg: 'bg-emerald-100 text-emerald-800 border-emerald-300',
        barColor: 'bg-emerald-500',
        textColor: 'text-emerald-700'
      };
    } else if (cat.includes('Slight')) {
      return {
        badgeBg: 'bg-amber-100 text-amber-800 border-amber-300',
        barColor: 'bg-amber-500',
        textColor: 'text-amber-700'
      };
    } else if (cat.includes('Moderate')) {
      return {
        badgeBg: 'bg-orange-100 text-orange-800 border-orange-300',
        barColor: 'bg-orange-500',
        textColor: 'text-orange-700'
      };
    } else {
      return {
        badgeBg: 'bg-red-100 text-red-800 border-red-300',
        barColor: 'bg-red-600',
        textColor: 'text-red-700'
      };
    }
  };

  const theme = getCategoryTheme(delayCategory);

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Delay Assessment</span>
        <span className={`px-2.5 py-1 rounded-md text-xs font-bold border ${theme.badgeBg}`}>
          {delayCategory}
        </span>
      </div>

      <div className="flex items-baseline justify-between">
        <div>
          <span className="text-3xl font-extrabold text-slate-900">
            {predictedDelay > 0 ? `+${predictedDelay}` : predictedDelay}
          </span>
          <span className="ml-1 text-sm font-semibold text-slate-500">minutes</span>
        </div>
        <div className="text-right">
          <span className="text-xs text-slate-400 block">Late Probability</span>
          <span className={`text-xl font-bold ${latePercent > 50 ? 'text-red-600' : 'text-emerald-600'}`}>
            {latePercent}%
          </span>
        </div>
      </div>

      {/* Probability Progress Bar */}
      <div>
        <div className="flex justify-between text-[11px] font-semibold text-slate-500 mb-1">
          <span>On-Time Probability ({onTimePercent}%)</span>
          <span>Late Risk ({latePercent}%)</span>
        </div>
        <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden flex">
          <div
            className="bg-emerald-500 h-full transition-all duration-500"
            style={{ width: `${onTimePercent}%` }}
          />
          <div
            className="bg-red-500 h-full transition-all duration-500"
            style={{ width: `${latePercent}%` }}
          />
        </div>
      </div>

      {/* Uncertainty Range */}
      <div className="bg-slate-50 rounded-lg p-3 border border-slate-100 flex items-center justify-between text-xs">
        <div>
          <span className="text-slate-500 block text-[11px]">90% Confidence Interval</span>
          <span className="font-semibold text-slate-700">
            Between {confidenceLower}m and {confidenceUpper}m
          </span>
        </div>
        <div className="text-right text-[11px] text-slate-400">
          $\pm$ {Math.round((confidenceUpper - confidenceLower) / 2)}m spread
        </div>
      </div>
    </div>
  );
};
