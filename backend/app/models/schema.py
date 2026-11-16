import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text, JSON, Index
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Station(Base):
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True, index=True)
    station_code = Column(String(10), unique=True, index=True, nullable=False)
    station_name = Column(String(100), nullable=False)
    zone = Column(String(20), nullable=True)         # NR, WR, CR, ER, SR, etc.
    state = Column(String(50), nullable=True)
    division = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Relationships
    routes = relationship("TrainRoute", back_populates="station")

class Train(Base):
    __tablename__ = "trains"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), unique=True, index=True, nullable=False)
    train_name = Column(String(120), nullable=False)
    train_category = Column(String(50), nullable=False) # Rajdhani, Shatabdi, Vande Bharat, Superfast, Mail/Express, Passenger
    source_station_code = Column(String(10), nullable=False)
    dest_station_code = Column(String(10), nullable=False)
    total_distance_km = Column(Float, default=0.0)
    runs_on_days = Column(String(30), default="Daily")  # e.g., Mon,Tue,Wed,Thu,Fri,Sat,Sun
    active = Column(Boolean, default=True)
    
    # Relationships
    routes = relationship("TrainRoute", back_populates="train", cascade="all, delete-orphan", order_by="TrainRoute.stop_number")
    schedules = relationship("TrainSchedule", back_populates="train", cascade="all, delete-orphan")

class TrainRoute(Base):
    __tablename__ = "train_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), ForeignKey("trains.train_number", ondelete="CASCADE"), nullable=False)
    station_code = Column(String(10), ForeignKey("stations.station_code"), nullable=False)
    stop_number = Column(Integer, nullable=False)
    scheduled_arrival = Column(String(10), nullable=True)   # "HH:MM"
    scheduled_departure = Column(String(10), nullable=True) # "HH:MM"
    halt_minutes = Column(Float, default=2.0)
    distance_from_source_km = Column(Float, default=0.0)
    day_offset = Column(Integer, default=1) # 1 = same day, 2 = next day
    
    train = relationship("Train", back_populates="routes")
    station = relationship("Station", back_populates="routes")

    __table_args__ = (
        Index("idx_train_stop", "train_number", "stop_number"),
    )

class TrainSchedule(Base):
    __tablename__ = "train_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), ForeignKey("trains.train_number", ondelete="CASCADE"), nullable=False)
    frequency = Column(String(50), default="Daily")
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    metadata_info = Column(JSON, nullable=True)
    
    train = relationship("Train", back_populates="schedules")

class HistoricalTrainRunning(Base):
    __tablename__ = "historical_train_running"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), index=True, nullable=False)
    train_name = Column(String(120), nullable=True)
    journey_date = Column(Date, index=True, nullable=False)
    station_code = Column(String(10), index=True, nullable=False)
    scheduled_arrival = Column(String(10), nullable=True)
    actual_arrival = Column(String(10), nullable=True)
    scheduled_departure = Column(String(10), nullable=True)
    actual_departure = Column(String(10), nullable=True)
    delay_arrival_minutes = Column(Float, default=0.0)
    delay_departure_minutes = Column(Float, default=0.0)
    distance_km = Column(Float, default=0.0)
    halt_duration_minutes = Column(Float, default=0.0)
    day_of_week = Column(String(15), nullable=True)
    train_category = Column(String(50), nullable=True)
    weather_condition = Column(String(50), nullable=True) # Fog, Rain, Clear
    congestion_level = Column(String(20), default="Normal") # Low, Normal, High
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("idx_train_date_station", "train_number", "journey_date", "station_code"),
    )

class DelayRecord(Base):
    __tablename__ = "delay_records"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), index=True, nullable=False)
    journey_date = Column(Date, nullable=False)
    station_code = Column(String(10), nullable=False)
    delay_minutes = Column(Float, nullable=False)
    delay_category = Column(String(30), nullable=False) # On-Time (<=15), Slight (15-45), Moderate (45-120), Severe (>120)
    primary_cause_guess = Column(String(100), nullable=True) # Signal congestion, Weather/Fog, Technical, Track maintenance
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)

class ImportedDataset(Base):
    __tablename__ = "imported_datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(120), nullable=False)
    file_type = Column(String(20), nullable=False) # csv, xlsx, json
    file_path = Column(String(255), nullable=True)
    total_records = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    invalid_records = Column(Integer, default=0)
    cleaning_summary = Column(JSON, nullable=True) # duplicates_dropped, nulls_imputed, outliers_handled
    status = Column(String(30), default="Pending") # Pending, Processing, Ready, Failed
    upload_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, index=True, nullable=False)
    model_type = Column(String(50), nullable=False) # LinearRegression, RandomForest, GradientBoosting, XGBoost
    model_version = Column(String(20), nullable=False)
    artifact_path = Column(String(255), nullable=False)
    scaler_artifact_path = Column(String(255), nullable=True)
    mae = Column(Float, nullable=False)
    mse = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2_score = Column(Float, nullable=False)
    is_active = Column(Boolean, default=False)
    features_list = Column(JSON, nullable=False)
    hyperparameters = Column(JSON, nullable=True)
    evaluation_metrics = Column(JSON, nullable=True)
    training_sample_count = Column(Integer, default=0)
    trained_at = Column(DateTime, default=datetime.datetime.utcnow)

class ModelTrainingHistory(Base):
    __tablename__ = "model_training_history"
    
    id = Column(Integer, primary_key=True, index=True)
    training_run_id = Column(String(50), unique=True, index=True, nullable=False)
    model_type = Column(String(50), nullable=False)
    dataset_id = Column(Integer, nullable=True)
    train_row_count = Column(Integer, default=0)
    test_row_count = Column(Integer, default=0)
    training_duration_seconds = Column(Float, default=0.0)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2 = Column(Float, nullable=False)
    status = Column(String(30), default="Completed") # Running, Completed, Failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class PredictionResult(Base):
    __tablename__ = "prediction_results"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(60), unique=True, index=True, nullable=False)
    train_number = Column(String(10), index=True, nullable=False)
    train_name = Column(String(120), nullable=True)
    source_station = Column(String(10), nullable=False)
    dest_station = Column(String(10), nullable=False)
    target_station = Column(String(10), nullable=False)
    journey_date = Column(Date, nullable=False)
    scheduled_arrival = Column(String(10), nullable=True)
    predicted_arrival_time = Column(String(10), nullable=True)
    predicted_delay_minutes = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float, default=0.0)
    confidence_interval_upper = Column(Float, default=0.0)
    late_probability = Column(Float, default=0.0) # 0.0 to 1.0
    delay_category = Column(String(30), nullable=False) # On-Time, Slight, Moderate, Severe
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(30), nullable=True)
    actual_delay_minutes = Column(Float, nullable=True) # Populated if actual running data arrives
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class PredictionFeature(Base):
    __tablename__ = "prediction_features"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(60), ForeignKey("prediction_results.prediction_id", ondelete="CASCADE"), nullable=False)
    feature_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default="viewer") # admin, analyst, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=True)
    action = Column(String(50), nullable=False) # LOGIN, UPLOAD_DATASET, RETRAIN_MODEL, ACTIVATE_MODEL, PREDICT
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
