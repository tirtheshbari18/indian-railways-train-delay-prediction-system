import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  MapPin, 
  Calendar, 
  CloudRain, 
  AlertCircle, 
  ArrowRight, 
  Sparkles, 
  ShieldAlert,
  Info,
  Train as TrainIcon
} from 'lucide-react';
import { api } from '../services/api';
import { Train, PredictionResponse } from '../types';
import { DelayGauge } from '../components/DelayGauge';

export const TrainDelayPrediction: React.FC = () => {
  const [trains, setTrains] = useState<Train[]>([]);
  const [selectedTrainNum, setSelectedTrainNum] = useState<string>('12951');
  const [currentTrain, setCurrentTrain] = useState<Train | null>(null);

  // Form State
  const [trainNumber, setTrainNumber] = useState<string>('12951');
  const [trainName, setTrainName] = useState<string>('Mumbai Tejas Rajdhani Express');
  const [sourceStation, setSourceStation] = useState<string>('MMCT');
  const [destStation, setDestStation] = useState<string>('NDLS');
  const [targetStation, setTargetStation] = useState<string>('NDLS');
  const [journeyDate, setJourneyDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [scheduledDep, setScheduledDep] = useState<string>('17:00');
  const [scheduledArr, setScheduledArr] = useState<string>('08:32');
  const [previousDelay, setPreviousDelay] = useState<number>(0);
  const [weatherCondition, setWeatherCondition] = useState<string>('Clear');
  const [congestionLevel, setCongestionLevel] = useState<string>('Normal');

  // Prediction Result
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [predicting, setPredicting] = useState<boolean>(false);
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
        handleSelectTrain(safeData[0]);
      }
    } catch (e) {
      console.error('Failed to load trains', e);
    }
  };

  const handleSelectTrain = (tr: Train) => {
    setSelectedTrainNum(tr.train_number);
    setCurrentTrain(tr);
    setTrainNumber(tr.train_number);
    setTrainName(tr.train_name);
    setSourceStation(tr.source_station_code);
    setDestStation(tr.dest_station_code);
    setTargetStation(tr.dest_station_code);

    // Auto-fill times from routes if present
    if (tr.routes && tr.routes.length > 0) {
      const origin = tr.routes[0];
      const finalStop = tr.routes[tr.routes.length - 1];
      if (origin.scheduled_departure) setScheduledDep(origin.scheduled_departure);
      if (finalStop.scheduled_arrival) setScheduledArr(finalStop.scheduled_arrival);
    }
  };

  const onTrainDropdownChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const num = e.target.value;
    setSelectedTrainNum(num);
    try {
      const details = await api.getTrainDetails(num);
      handleSelectTrain(details);
    } catch {
      const found = trains.find(t => t.train_number === num);
      if (found) handleSelectTrain(found);
    }
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setPredicting(true);
    setErrorMsg(null);
    try {
      const res = await api.predictDelay({
        train_number: trainNumber,
        train_name: trainName,
        source_station: sourceStation,
        destination_station: destStation,
        target_station: targetStation,
        journey_date: journeyDate,
        scheduled_departure: scheduledDep,
        scheduled_arrival: scheduledArr,
        previous_station_delay: Number(previousDelay),
        weather_condition: weatherCondition,
        congestion_level: congestionLevel,
        train_category: currentTrain?.train_category || 'Express',
      });
      setPrediction(res);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to generate delay prediction.');
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div>
        <span className="text-xs uppercase font-bold tracking-widest text-railway-blue">AI Regression Engine</span>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Train Delay Prediction Portal</h2>
        <p className="text-sm text-slate-600">
          Enter voyage parameters, previous checkpoint delays and meteorological conditions to compute estimated arrival delay.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Prediction Input Form */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <form onSubmit={handlePredict} className="space-y-4">
            
            {/* Quick Train Selector */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Select Premier / Express Train
              </label>
              <select
                value={selectedTrainNum}
                onChange={onTrainDropdownChange}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-railway-blue focus:bg-white"
              >
                {(Array.isArray(trains) ? trains : []).map((t) => (
                  <option key={t.train_number} value={t.train_number}>
                    {t.train_number} - {t.train_name} ({t.train_category}) [{t.source_station_code} → {t.dest_station_code}]
                  </option>
                ))}
              </select>
            </div>

            {/* Custom Train Number & Name */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Train Number</label>
                <input
                  type="text"
                  value={trainNumber}
                  onChange={(e) => setTrainNumber(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-railway-blue"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Train Name</label>
                <input
                  type="text"
                  value={trainName}
                  onChange={(e) => setTrainName(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-railway-blue"
                  required
                />
              </div>
            </div>

            {/* Stations: Source, Destination, Target */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Origin Station</label>
                <input
                  type="text"
                  value={sourceStation}
                  onChange={(e) => setSourceStation(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg font-mono uppercase"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Final Destination</label>
                <input
                  type="text"
                  value={destStation}
                  onChange={(e) => setDestStation(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg font-mono uppercase"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Target Checkpoint</label>
                <input
                  type="text"
                  value={targetStation}
                  onChange={(e) => setTargetStation(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 text-sm bg-blue-50/50 border border-blue-200 rounded-lg font-mono uppercase font-bold text-railway-blue"
                  title="Intermediate station or final destination for prediction"
                  required
                />
              </div>
            </div>

            {/* Date and Timings */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Journey Date</label>
                <input
                  type="date"
                  value={journeyDate}
                  onChange={(e) => setJourneyDate(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Scheduled Dep (HH:MM)</label>
                <input
                  type="text"
                  value={scheduledDep}
                  onChange={(e) => setScheduledDep(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg font-mono"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Scheduled Arr (HH:MM)</label>
                <input
                  type="text"
                  value={scheduledArr}
                  onChange={(e) => setScheduledArr(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg font-mono"
                  required
                />
              </div>
            </div>

            {/* Previous Delay, Weather, Congestion */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  Previous Delay (mins)
                </label>
                <input
                  type="number"
                  min="-20"
                  max="720"
                  value={previousDelay}
                  onChange={(e) => setPreviousDelay(Number(e.target.value))}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
                />
                <span className="text-[10px] text-slate-400">Delay at previous station</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Weather Condition</label>
                <select
                  value={weatherCondition}
                  onChange={(e) => setWeatherCondition(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
                >
                  <option value="Clear">Clear / Standard</option>
                  <option value="Rain">Monsoon / Rain</option>
                  <option value="Heavy Rain">Heavy Torrential Rain</option>
                  <option value="Fog">Moderate Winter Fog</option>
                  <option value="Dense Fog">Dense Fog (Speed Limit)</option>
                </select>
                <span className="text-[10px] text-slate-400">Seasonal visibility factor</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Junction Congestion</label>
                <select
                  value={congestionLevel}
                  onChange={(e) => setCongestionLevel(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
                >
                  <option value="Low">Low Line Utilization</option>
                  <option value="Normal">Normal Traffic Density</option>
                  <option value="High">High Freight / Passenger Mix</option>
                  <option value="Severe">Severe Bottleneck (&gt;140%)</option>
                </select>
                <span className="text-[10px] text-slate-400">Signal block utilization</span>
              </div>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Submit Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={predicting}
                className="w-full py-3 bg-railway-navy hover:bg-railway-blue text-white font-bold text-sm rounded-xl transition-all shadow-md flex items-center justify-center space-x-2 disabled:opacity-70"
              >
                {predicting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Executing ML Prediction Pipeline...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    <span>Generate AI Delay Prediction</span>
                  </>
                )}
              </button>
            </div>

          </form>
        </div>

        {/* Prediction Results Display */}
        <div className="lg:col-span-5 space-y-4">
          
          {prediction ? (
            <div className="space-y-4">
              
              {/* Main Expected Arrival Card */}
              <div className="bg-gradient-to-br from-railway-navy to-railway-steel text-white rounded-xl p-6 shadow-md relative overflow-hidden">
                <div className="flex items-center justify-between text-xs text-blue-200 font-semibold mb-2">
                  <span>PREDICTION ID: {prediction.prediction_id}</span>
                  <span className="px-2 py-0.5 rounded bg-blue-500/20 border border-blue-400/30">
                    {prediction.model_name}
                  </span>
                </div>

                <div className="mt-2">
                  <span className="text-xs text-slate-300 uppercase tracking-wider">Estimated Arrival at {prediction.target_station}</span>
                  <div className="text-4xl font-extrabold text-white mt-1">
                    {prediction.predicted_arrival_time}
                  </div>
                  <div className="text-xs text-slate-300 mt-1 flex items-center gap-2">
                    <span>Scheduled: {prediction.scheduled_arrival}</span>
                    <span>•</span>
                    <span className="text-amber-300 font-bold">
                      Expected Delay: {prediction.predicted_delay_minutes > 0 ? `+${prediction.predicted_delay_minutes}` : prediction.predicted_delay_minutes} mins
                    </span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between text-xs">
                  <div>
                    <span className="text-slate-300 block text-[10px]">TRAIN</span>
                    <span className="font-semibold text-white">{prediction.train_name} ({prediction.train_number})</span>
                  </div>
                  <div className="text-right">
                    <span className="text-slate-300 block text-[10px]">ROUTE</span>
                    <span className="font-semibold text-white">{prediction.source_station} → {prediction.destination_station}</span>
                  </div>
                </div>
              </div>

              {/* Delay Gauge & Uncertainty Card */}
              <DelayGauge
                lateProbability={prediction.late_probability}
                predictedDelay={prediction.predicted_delay_minutes}
                confidenceLower={prediction.confidence_interval.lower}
                confidenceUpper={prediction.confidence_interval.upper}
                delayCategory={prediction.delay_category}
              />

              {/* Explanatory AI Insights */}
              <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
                <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 uppercase tracking-wider">
                  <Info className="w-4 h-4 text-railway-blue" />
                  <span>AI Operational Insights</span>
                </div>
                <div className="space-y-2">
                  {(Array.isArray(prediction.explanation) ? prediction.explanation : []).map((exp, idx) => (
                    <div key={idx} className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100 flex items-start space-x-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-railway-blue mt-1.5 shrink-0" />
                      <span>{exp}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Crucial AI Disclaimer Requirement */}
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 flex items-start space-x-3">
                <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-amber-800">Operational Disclaimer</div>
                  <p className="text-[11px] text-amber-700 mt-0.5 leading-relaxed">
                    {prediction.disclaimer} This estimate is derived from gradient-boosted historical pattern analysis and does not replace live GPS or station master control feeds.
                  </p>
                </div>
              </div>

            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-10 text-center space-y-3 shadow-sm">
              <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
                <Clock className="w-6 h-6 text-railway-blue" />
              </div>
              <h4 className="text-base font-bold text-slate-800">Ready for Prediction</h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Select your train, verify route details, and configure optional weather or checkpoint delays to run machine learning estimation.
              </p>
            </div>
          )}

        </div>

      </div>

    </div>
  );
};
