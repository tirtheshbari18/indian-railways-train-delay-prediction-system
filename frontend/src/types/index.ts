export interface Station {
  station_code: string;
  station_name: string;
  zone?: string;
  state?: string;
  division?: string;
  latitude?: number;
  longitude?: number;
}

export interface RouteStop {
  station_code: string;
  station_name?: string;
  stop_number: number;
  scheduled_arrival?: string;
  scheduled_departure?: string;
  halt_minutes: number;
  distance_from_source_km: number;
  day_offset: number;
}

export interface Train {
  train_number: string;
  train_name: string;
  train_category: string;
  source_station_code: string;
  dest_station_code: string;
  total_distance_km: number;
  runs_on_days: string;
  active: boolean;
  routes?: RouteStop[];
}

export interface PredictionRequest {
  train_number: string;
  train_name?: string;
  source_station: string;
  destination_station: string;
  target_station?: string;
  journey_date: string;
  scheduled_departure?: string;
  scheduled_arrival?: string;
  previous_station_delay?: number;
  weather_condition?: string;
  congestion_level?: string;
  train_category?: string;
}

export interface PredictionResponse {
  prediction_id: string;
  train_number: string;
  train_name: string;
  source_station: string;
  destination_station: string;
  target_station: string;
  journey_date: string;
  scheduled_arrival: string;
  predicted_arrival_time: string;
  predicted_delay_minutes: number;
  confidence_interval: {
    lower: number;
    upper: number;
  };
  late_probability: number;
  delay_category: string;
  model_name: string;
  model_version: string;
  explanation: string[];
  disclaimer: string;
}

export interface IntermediateStationPrediction {
  station_code: string;
  station_name: string;
  stop_number: number;
  scheduled_arrival?: string;
  scheduled_departure?: string;
  predicted_arrival_time: string;
  predicted_arrival_delay_minutes: number;
  cumulative_delay_minutes: number;
  delay_change_minutes: number;
  late_probability: number;
  delay_category: string;
  distance_km: number;
}

export interface RoutePredictionResponse {
  train_number: string;
  train_name: string;
  source_station: string;
  destination_station: string;
  journey_date: string;
  initial_departure_delay: number;
  final_predicted_delay_minutes: number;
  final_scheduled_arrival: string;
  final_predicted_arrival: string;
  total_distance_km: number;
  intermediate_stations: IntermediateStationPrediction[];
  high_risk_segments: string[];
  recovery_opportunities: string[];
}

export interface DashboardKPIs {
  total_trains_analysed: number;
  total_predictions_generated: number;
  average_predicted_delay_min: number;
  on_time_performance_pct: number;
  delayed_train_pct: number;
  severe_delay_pct: number;
  active_model_name: string;
  model_mae: number;
  model_r2: number;
  latest_dataset_update?: string;
}

export interface MostDelayedTrain {
  train_number: string;
  train_name: string;
  train_category: string;
  route: string;
  average_delay_minutes: number;
  delay_frequency_pct: number;
  total_runs: number;
}

export interface HighDelaySection {
  section_name: string;
  zone: string;
  average_delay_minutes: number;
  incident_count: number;
  primary_factor: string;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
}

export interface StationDelayItem {
  station_code: string;
  station_name: string;
  zone: string;
  avg_arrival_delay: number;
  recurring_delay_pct: number;
  congestion_score: number;
}

export interface DelayTrendItem {
  date: string;
  avg_delay_minutes: number;
  total_trains: number;
  on_time_pct: number;
}

export interface ActualVsPredictedItem {
  train_number: string;
  station_code: string;
  journey_date: string;
  actual_delay: number;
  predicted_delay: number;
  error_minutes: number;
}

export interface DatasetSummary {
  id: number;
  dataset_name: string;
  file_type: string;
  total_records: number;
  valid_records: number;
  invalid_records: number;
  cleaning_summary?: Record<string, any>;
  status: string;
  upload_timestamp: string;
  notes?: string;
}

export interface HistoricalRunningRecord {
  id: number;
  train_number: string;
  train_name?: string;
  journey_date: string;
  station_code: string;
  scheduled_arrival?: string;
  actual_arrival?: string;
  scheduled_departure?: string;
  actual_departure?: string;
  delay_arrival_minutes: number;
  delay_departure_minutes: number;
  distance_km: number;
  day_of_week?: string;
  train_category?: string;
}

export interface ModelRegistryItem {
  id: number;
  model_name: string;
  model_type: string;
  model_version: string;
  mae: number;
  mse: number;
  rmse: number;
  r2_score: number;
  is_active: boolean;
  features_list: string[];
  training_sample_count: number;
  trained_at: string;
}

export interface PredictionHistoryItem {
  prediction_id: string;
  train_number: string;
  train_name: string;
  source_station: string;
  dest_station: string;
  target_station: string;
  journey_date: string;
  scheduled_arrival: string;
  predicted_arrival_time: string;
  predicted_delay_minutes: number;
  confidence_interval: {
    lower: number;
    upper: number;
  };
  late_probability: number;
  delay_category: string;
  model_name: string;
  actual_delay_minutes?: number;
  created_at: string;
}
