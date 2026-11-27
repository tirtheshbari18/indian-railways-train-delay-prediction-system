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

// ----------------- Comprehensive Indian Railways Master Types -----------------
export interface TrainBetweenStationsResult {
  train_number: string;
  train_name: string;
  train_category: string;
  train_type: string;
  runs_on_days: string;
  source_code: string;
  source_name: string;
  source_departure: string;
  source_platform?: string;
  dest_code: string;
  dest_name: string;
  dest_arrival: string;
  dest_platform?: string;
  travel_distance_km: number;
  travel_duration_minutes: number;
  travel_duration_str: string;
  intermediate_stops_count: number;
  is_commercial_stop: boolean;
}

export interface LiveRunningStop {
  stop_number: number;
  station_code: string;
  station_name: string;
  scheduled_arrival?: string;
  scheduled_departure?: string;
  actual_arrival?: string;
  actual_departure?: string;
  delay_arrival_minutes: number;
  delay_departure_minutes: number;
  platform: string;
  distance_km: number;
  status: 'Departed' | 'Current' | 'Next' | 'Upcoming';
}

export interface LiveTrainRunningResponse {
  train_number: string;
  train_name: string;
  train_category: string;
  source_station_code: string;
  source_station_name: string;
  dest_station_code: string;
  dest_station_name: string;
  current_status: string;
  current_station_code: string;
  current_station_name: string;
  delay_minutes: number;
  delay_category: string;
  last_reported_time: string;
  timeline: LiveRunningStop[];
}

export interface StationPlatform {
  id?: number;
  station_code: string;
  platform_number: string;
  platform_length_m?: number;
  platform_type: string;
  electrification: boolean;
  line_identifier?: string;
  status: string;
}

export interface StationDetail {
  station_code: string;
  station_name: string;
  alternative_names: string[];
  zone?: string;
  division?: string;
  state?: string;
  district?: string;
  city?: string;
  station_category?: string;
  station_type?: string;
  latitude?: number;
  longitude?: number;
  elevation?: number;
  total_platforms: number;
  platform_identifiers?: string;
  lines_count: number;
  track_gauge?: string;
  electrification_status?: string;
  previous_station?: string;
  next_station?: string;
  dist_from_prev_km?: number;
  dist_to_next_km?: number;
  source?: string;
  platforms?: StationPlatform[];
}

export interface RailwayDivision {
  division_code: string;
  division_name: string;
  headquarters?: string;
  state?: string;
  route_km?: number;
}

export interface RailwayZone {
  zone_code: string;
  zone_name: string;
  headquarters: string;
  founded_year?: number;
  established_year?: number;
  total_route_km?: number;
  color_code?: string;
  active?: boolean;
  divisions: RailwayDivision[];
}

export interface RailwayDistance {
  from_station_code: string;
  to_station_code: string;
  distance_km: number;
  is_consecutive: boolean;
  cumulative_km: number;
  section_name?: string;
  line_identifier?: string;
  source?: string;
}

export interface OperationalEvent {
  id?: number;
  event_id?: string;
  station_code: string;
  station_name?: string;
  first_train_number: string;
  first_train_name?: string;
  second_train_number: string;
  second_train_name?: string;
  event_type: string;
  scheduled_time?: string;
  direction_first?: string;
  direction_second?: string;
  track_line?: string;
  verification_status?: string;
  confidence_level?: number;
  description?: string;
}

export interface MapNode {
  code: string;
  name: string;
  lat: number;
  lng: number;
  zone?: string;
  division?: string;
  platforms: number;
  category?: string;
  type?: string;
}

export interface MapEdge {
  from_code: string;
  to_code: string;
  distance_km: number;
  section?: string;
  coordinates: [[number, number], [number, number]];
}

export interface MapNetwork {
  nodes: MapNode[];
  edges: MapEdge[];
  total_stations: number;
  total_tracks: number;
}
