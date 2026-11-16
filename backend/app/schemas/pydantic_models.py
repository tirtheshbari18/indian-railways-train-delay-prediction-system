from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field

# ----------------- Auth Schemas -----------------
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "viewer"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ----------------- Station & Train Schemas -----------------
class StationSchema(BaseModel):
    station_code: str
    station_name: str
    zone: Optional[str] = None
    state: Optional[str] = None
    division: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    class Config:
        from_attributes = True

class RouteStopSchema(BaseModel):
    station_code: str
    station_name: Optional[str] = None
    stop_number: int
    scheduled_arrival: Optional[str] = None
    scheduled_departure: Optional[str] = None
    halt_minutes: float
    distance_from_source_km: float
    day_offset: int = 1
    class Config:
        from_attributes = True

class TrainSchema(BaseModel):
    train_number: str
    train_name: str
    train_category: str
    source_station_code: str
    dest_station_code: str
    total_distance_km: float
    runs_on_days: str
    active: bool = True
    class Config:
        from_attributes = True

class TrainDetailSchema(TrainSchema):
    routes: List[RouteStopSchema] = []

# ----------------- Prediction Schemas -----------------
class TrainDelayPredictionRequest(BaseModel):
    train_number: str
    train_name: Optional[str] = None
    source_station: str
    destination_station: str
    target_station: Optional[str] = None # Intermediate or final destination
    journey_date: date
    scheduled_departure: Optional[str] = "08:00" # HH:MM
    scheduled_arrival: Optional[str] = "14:30"   # HH:MM
    previous_station_delay: Optional[float] = 0.0 # Delay at previous station in minutes
    weather_condition: Optional[str] = "Clear" # Fog, Rain, Clear
    congestion_level: Optional[str] = "Normal" # Low, Normal, High
    train_category: Optional[str] = None

class TrainDelayPredictionResponse(BaseModel):
    prediction_id: str
    train_number: str
    train_name: str
    source_station: str
    destination_station: str
    target_station: str
    journey_date: date
    scheduled_arrival: str
    predicted_arrival_time: str
    predicted_delay_minutes: float
    confidence_interval: Dict[str, float] # {"lower": x, "upper": y}
    late_probability: float # e.g. 0.85
    delay_category: str # "On-Time (0-15m)", "Slight (15-45m)", "Moderate (45-120m)", "Severe (>120m)"
    model_name: str
    model_version: str
    explanation: List[str]
    disclaimer: str = "AI ML Prediction estimate based on historical patterns, not real-time GPS tracking."

class IntermediateStationPrediction(BaseModel):
    station_code: str
    station_name: str
    stop_number: int
    scheduled_arrival: Optional[str]
    scheduled_departure: Optional[str]
    predicted_arrival_time: str
    predicted_arrival_delay_minutes: float
    cumulative_delay_minutes: float
    delay_change_minutes: float # Compounding or recovery compared to previous stop
    late_probability: float
    delay_category: str
    distance_km: float

class RouteDelayPredictionRequest(BaseModel):
    train_number: str
    journey_date: date
    initial_delay_minutes: Optional[float] = 0.0
    weather_condition: Optional[str] = "Clear"

class RouteDelayPredictionResponse(BaseModel):
    train_number: str
    train_name: str
    source_station: str
    destination_station: str
    journey_date: date
    initial_departure_delay: float
    final_predicted_delay_minutes: float
    final_scheduled_arrival: str
    final_predicted_arrival: str
    total_distance_km: float
    intermediate_stations: List[IntermediateStationPrediction]
    high_risk_segments: List[str]
    recovery_opportunities: List[str]

# ----------------- Historical Data & Datasets -----------------
class DatasetSummary(BaseModel):
    id: int
    dataset_name: str
    file_type: str
    total_records: int
    valid_records: int
    invalid_records: int
    cleaning_summary: Optional[Dict[str, Any]]
    status: str
    upload_timestamp: datetime
    notes: Optional[str]
    class Config:
        from_attributes = True

class HistoricalRunningRecord(BaseModel):
    id: int
    train_number: str
    train_name: Optional[str]
    journey_date: date
    station_code: str
    scheduled_arrival: Optional[str]
    actual_arrival: Optional[str]
    scheduled_departure: Optional[str]
    actual_departure: Optional[str]
    delay_arrival_minutes: float
    delay_departure_minutes: float
    distance_km: float
    day_of_week: Optional[str]
    train_category: Optional[str]
    class Config:
        from_attributes = True

# ----------------- Model Registry & Training -----------------
class ModelTrainRequest(BaseModel):
    model_types: List[str] = ["LinearRegression", "RandomForest", "GradientBoosting", "XGBoost"]
    test_size: float = Field(0.2, ge=0.1, le=0.4)
    auto_activate_best: bool = False

class ModelMetrics(BaseModel):
    model_type: str
    model_name: str
    mae: float
    mse: float
    rmse: float
    r2_score: float
    is_active: bool
    trained_at: datetime
    features_used: List[str]
    training_sample_count: int

class ModelRegistryItem(BaseModel):
    id: int
    model_name: str
    model_type: str
    model_version: str
    mae: float
    mse: float
    rmse: float
    r2_score: float
    is_active: bool
    features_list: List[str]
    training_sample_count: int
    trained_at: datetime
    class Config:
        from_attributes = True

class ModelActivateRequest(BaseModel):
    model_name: str

# ----------------- Dashboard & Analytics -----------------
class DashboardKPIs(BaseModel):
    total_trains_analysed: int
    total_predictions_generated: int
    average_predicted_delay_min: float
    on_time_performance_pct: float
    delayed_train_pct: float
    severe_delay_pct: float
    active_model_name: str
    model_mae: float
    model_r2: float
    latest_dataset_update: Optional[datetime]

class MostDelayedTrain(BaseModel):
    train_number: str
    train_name: str
    train_category: str
    route: str
    average_delay_minutes: float
    delay_frequency_pct: float
    total_runs: int

class HighDelaySection(BaseModel):
    section_name: str
    zone: str
    average_delay_minutes: float
    incident_count: int
    primary_factor: str
    risk_level: str # Low, Medium, High, Critical

class DelayTrendItem(BaseModel):
    date: str
    avg_delay_minutes: float
    total_trains: int
    on_time_pct: float

class StationDelayItem(BaseModel):
    station_code: str
    station_name: str
    zone: str
    avg_arrival_delay: float
    recurring_delay_pct: float
    congestion_score: float

class ActualVsPredictedItem(BaseModel):
    train_number: str
    station_code: str
    journey_date: str
    actual_delay: float
    predicted_delay: float
    error_minutes: float
