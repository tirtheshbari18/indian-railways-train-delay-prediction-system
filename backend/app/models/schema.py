import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text, JSON, Index
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

# ============================================================================
# MODULE 11: 28 NORMALIZED CORE INDIAN RAILWAYS TABLES
# ============================================================================

# 1. railway_zones
class RailwayZone(Base):
    __tablename__ = "railway_zones"
    
    zone_code = Column(String(10), primary_key=True, index=True) # e.g. WR, CR, NR
    zone_name = Column(String(100), nullable=False)               # e.g. Western Railway
    headquarters = Column(String(100), nullable=False)            # e.g. Mumbai (Churchgate)
    established_year = Column(Integer, nullable=True)
    total_route_km = Column(Float, default=0.0)
    color_code = Column(String(20), default="#1E3E62")
    active = Column(Boolean, default=True)
    
    divisions = relationship("RailwayDivision", back_populates="zone", cascade="all, delete-orphan")

# 2. railway_divisions
class RailwayDivision(Base):
    __tablename__ = "railway_divisions"
    
    division_code = Column(String(20), primary_key=True, index=True) # e.g. BCT, ADI, BRC
    division_name = Column(String(100), nullable=False)              # e.g. Mumbai WR
    zone_code = Column(String(10), ForeignKey("railway_zones.zone_code"), nullable=False)
    headquarters = Column(String(100), nullable=False)
    state = Column(String(50), nullable=True)
    
    zone = relationship("RailwayZone", back_populates="divisions")

# 3. stations (Master Station Table)
class Station(Base):
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True, index=True)
    station_code = Column(String(10), unique=True, index=True, nullable=False)
    station_name = Column(String(100), nullable=False)
    alternative_names = Column(JSON, nullable=True) # e.g. ["Bombay Central", "Mumbai Central Jn"]
    state = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    zone = Column(String(20), nullable=True)         # NR, WR, CR, ER, SR, etc.
    division = Column(String(50), nullable=True)
    station_category = Column(String(20), default="NSG-2") # NSG-1 to NSG-6, SG, HG
    station_type = Column(String(30), default="Regular")   # Terminal, Junction, Regular, Suburban, Halt
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    elevation = Column(Float, default=15.0)                # Metres above sea level
    total_platforms = Column(Integer, default=2)
    platform_identifiers = Column(String(100), default="1,2")
    platform_lengths = Column(JSON, nullable=True)         # {"1": 600, "2": 600} in metres
    lines_count = Column(Integer, default=2)
    track_gauge = Column(String(30), default="Broad Gauge (1676 mm)")
    electrification_status = Column(String(50), default="Electrified (25 kV AC)")
    railway_section = Column(String(100), nullable=True)
    previous_station = Column(String(10), nullable=True)
    next_station = Column(String(10), nullable=True)
    dist_from_prev_km = Column(Float, default=0.0)
    dist_to_next_km = Column(Float, default=0.0)
    junction_connections = Column(JSON, nullable=True)
    yard_cabin_connections = Column(JSON, nullable=True)
    source = Column(String(100), default="CRIS / Indian Railways Official")
    last_verified = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    routes = relationship("TrainRoute", back_populates="station")
    platforms = relationship("StationPlatform", back_populates="station", cascade="all, delete-orphan")
    aliases = relationship("StationAlias", back_populates="station", cascade="all, delete-orphan")

# 4. station_aliases
class StationAlias(Base):
    __tablename__ = "station_aliases"
    
    id = Column(Integer, primary_key=True, index=True)
    station_code = Column(String(10), ForeignKey("stations.station_code"), nullable=False, index=True)
    alias_name = Column(String(100), nullable=False)
    alias_type = Column(String(30), default="Vernacular") # Vernacular, Historical, Hindi, Regional
    
    station = relationship("Station", back_populates="aliases")

# 5. station_platforms
class StationPlatform(Base):
    __tablename__ = "station_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    station_code = Column(String(10), ForeignKey("stations.station_code"), nullable=False, index=True)
    platform_number = Column(String(10), nullable=False) # e.g. "1", "2A", "10"
    platform_length_m = Column(Float, default=600.0)
    platform_type = Column(String(30), default="Island") # Island, Side, Terminal Bay
    electrification = Column(Boolean, default=True)
    track_gauge = Column(String(30), default="Broad Gauge")
    line_identifier = Column(String(50), nullable=True)  # Up Fast, Down Slow, Main
    status = Column(String(20), default="Operational")   # Operational, Maintenance
    
    station = relationship("Station", back_populates="platforms")

# 6. railway_lines
class RailwayLine(Base):
    __tablename__ = "railway_lines"
    
    line_id = Column(String(50), primary_key=True, index=True) # e.g. WR-MAIN-TRUNK
    line_name = Column(String(100), nullable=False)             # Mumbai Central - Ahmedabad Mainline
    gauge = Column(String(30), default="Broad Gauge")
    electrification = Column(String(50), default="25 kV AC OHE")
    tracks_count = Column(String(30), default="Double Line")   # Single Line, Double Line, Quadruple Line
    speed_limit_kmh = Column(Integer, default=130)

# 7. railway_sections
class RailwaySection(Base):
    __tablename__ = "railway_sections"
    
    section_code = Column(String(50), primary_key=True, index=True) # e.g. SEC-VR-DRD
    section_name = Column(String(120), nullable=False)              # Virar - Dahanu Road Section
    zone_code = Column(String(10), nullable=True)
    division_code = Column(String(20), nullable=True)
    from_station_code = Column(String(10), nullable=False)
    to_station_code = Column(String(10), nullable=False)
    distance_km = Column(Float, nullable=False)
    track_type = Column(String(30), default="Double Line")
    electrification = Column(String(50), default="Electrified")
    max_permissible_speed = Column(Integer, default=130)
    line_capacity_pct = Column(Float, default=115.0)

# 8. railway_track_segments
class RailwayTrackSegment(Base):
    __tablename__ = "railway_track_segments"
    
    segment_id = Column(String(60), primary_key=True, index=True)
    section_code = Column(String(50), ForeignKey("railway_sections.section_code"), nullable=False)
    geometry_geojson = Column(JSON, nullable=True) # LineString geometry coordinates [[lng, lat], ...]
    coordinates_json = Column(JSON, nullable=True)
    distance_km = Column(Float, default=0.0)
    speed_limit_kmh = Column(Integer, default=110)
    is_bridge = Column(Boolean, default=False)
    is_tunnel = Column(Boolean, default=False)

# 9. railway_connections
class RailwayConnection(Base):
    __tablename__ = "railway_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    from_station_code = Column(String(10), nullable=False, index=True)
    to_station_code = Column(String(10), nullable=False, index=True)
    connection_type = Column(String(30), default="Main Track") # Main Track, Branch, Chord Line, Yard Crossover
    is_bidirectional = Column(Boolean, default=True)

# 10. railway_distances
class RailwayDistance(Base):
    __tablename__ = "railway_distances"
    
    id = Column(Integer, primary_key=True, index=True)
    from_station_code = Column(String(10), nullable=False, index=True)
    to_station_code = Column(String(10), nullable=False, index=True)
    is_consecutive = Column(Boolean, default=True)
    distance_km = Column(Float, nullable=False)
    cumulative_km = Column(Float, default=0.0)
    section_name = Column(String(100), nullable=True)
    line_identifier = Column(String(50), nullable=True)
    source = Column(String(100), default="Official Working Timetable (WTT) / RBS Chainage")
    last_verified = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("idx_railway_dist_stations", "from_station_code", "to_station_code"),
    )

# 11. trains
class Train(Base):
    __tablename__ = "trains"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), unique=True, index=True, nullable=False)
    train_name = Column(String(120), nullable=False)
    alternative_names = Column(JSON, nullable=True) # e.g. ["Gujarat Superfast", "Gujarat Express"]
    train_category = Column(String(50), nullable=False) # Rajdhani, Shatabdi, Vande Bharat, Superfast, Mail/Express, MEMU, Passenger, Special
    train_type = Column(String(40), default="Express")  # SF, Express, Local, MEMU, EMU, Passenger, Special
    train_frequency = Column(String(40), default="Daily") # Daily, Weekly, 6 Days a Week, Bi-weekly
    source_station_code = Column(String(10), nullable=False, index=True)
    dest_station_code = Column(String(10), nullable=False, index=True)
    total_distance_km = Column(Float, default=0.0)
    total_duration_minutes = Column(Integer, default=0)
    runs_on_days = Column(String(30), default="Daily")  # Mon,Tue,Wed,Thu,Fri,Sat,Sun
    operating_period = Column(String(50), default="Regular Year-Round") # Regular, Summer Special, Festival Special
    effective_timetable_date = Column(String(30), default="2026-01-01")
    cancellation_status = Column(String(30), default="Running") # Running, Cancelled, Partially Cancelled
    diversion_info = Column(String(200), nullable=True)
    return_train_number = Column(String(10), nullable=True)
    data_source = Column(String(100), default="National Train Enquiry System (NTES) / CRIS")
    last_verified = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # Relationships
    routes = relationship("TrainRoute", back_populates="train", cascade="all, delete-orphan", order_by="TrainRoute.stop_number")
    stops = relationship("TrainRouteStop", back_populates="train", cascade="all, delete-orphan", order_by="TrainRouteStop.stop_number")
    schedules = relationship("TrainSchedule", back_populates="train", cascade="all, delete-orphan")
    category_mappings = relationship("TrainCategoryMapping", back_populates="train", cascade="all, delete-orphan")

# 12. train_categories
class TrainCategory(Base):
    __tablename__ = "train_categories"
    
    category_code = Column(String(30), primary_key=True, index=True) # e.g. VANDE_BHARAT, RAJDHANI, SF, MEMU
    category_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    service_class = Column(String(50), default="Premier") # Premier, High Priority, Mail/Express, Suburban, Passenger
    priority_rank = Column(Integer, default=5)            # 1 = Highest (Vande Bharat/Rajdhani) to 10 (Freight)

# 13. train_category_mapping
class TrainCategoryMapping(Base):
    __tablename__ = "train_category_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), ForeignKey("trains.train_number", ondelete="CASCADE"), nullable=False, index=True)
    category_code = Column(String(30), ForeignKey("train_categories.category_code"), nullable=False)
    is_primary = Column(Boolean, default=True)
    
    train = relationship("Train", back_populates="category_mappings")

# 14. train_running_days
class TrainRunningDay(Base):
    __tablename__ = "train_running_days"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), ForeignKey("trains.train_number", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(String(10), nullable=False) # Mon, Tue, Wed, Thu, Fri, Sat, Sun
    runs = Column(Boolean, default=True)

# 15. train_routes (Route Header)
class TrainRouteHeader(Base):
    __tablename__ = "train_route_headers"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), ForeignKey("trains.train_number", ondelete="CASCADE"), nullable=False, index=True)
    route_id = Column(String(30), default="MAIN")
    route_variant = Column(String(50), default="Standard Mainline")
    total_stops = Column(Integer, default=0)
    total_distance_km = Column(Float, default=0.0)

# 16. train_route_stops & backward-compatible TrainRoute
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
    distance_from_prev_km = Column(Float, default=0.0)
    day_offset = Column(Integer, default=1) # 1 = same day, 2 = next day
    verified_platform = Column(String(10), nullable=True) # e.g. "1", "3", "Not Available"
    is_commercial_stop = Column(Boolean, default=True)
    is_technical_stop = Column(Boolean, default=False)
    line_identifier = Column(String(30), nullable=True)
    
    train = relationship("Train", back_populates="routes")
    station = relationship("Station", back_populates="routes")

    __table_args__ = (
        Index("idx_train_stop", "train_number", "stop_number"),
        Index("idx_train_station", "train_number", "station_code"),
    )

class TrainRouteStop(Base):
    __tablename__ = "train_route_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), ForeignKey("trains.train_number", ondelete="CASCADE"), nullable=False, index=True)
    stop_number = Column(Integer, nullable=False)
    station_code = Column(String(10), nullable=False, index=True)
    station_name = Column(String(100), nullable=True)
    scheduled_arrival = Column(String(10), nullable=True)   # 24-hr "HH:MM"
    scheduled_departure = Column(String(10), nullable=True) # 24-hr "HH:MM"
    halt_minutes = Column(Float, default=2.0)
    distance_from_source_km = Column(Float, default=0.0)
    distance_from_prev_km = Column(Float, default=0.0)
    day_offset = Column(Integer, default=1)
    verified_platform = Column(String(10), default="Not Available")
    is_commercial_stop = Column(Boolean, default=True)
    is_technical_stop = Column(Boolean, default=False)
    line_identifier = Column(String(30), nullable=True)
    
    train = relationship("Train", back_populates="stops")

    __table_args__ = (
        Index("idx_route_stops_query", "train_number", "stop_number"),
    )

# 17. train_schedules
class TrainSchedule(Base):
    __tablename__ = "train_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), ForeignKey("trains.train_number", ondelete="CASCADE"), nullable=False, index=True)
    frequency = Column(String(50), default="Daily")
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    timetable_version = Column(String(30), default="2026-v1.0")
    metadata_info = Column(JSON, nullable=True)
    
    train = relationship("Train", back_populates="schedules")

# 18. train_special_periods
class TrainSpecialPeriod(Base):
    __tablename__ = "train_special_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), ForeignKey("trains.train_number", ondelete="CASCADE"), nullable=False, index=True)
    special_type = Column(String(50), nullable=False) # Festival Special, Holi Special, Diwali Special, Summer Special
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=False)
    operating_notes = Column(Text, nullable=True)

# 19. train_cancellations
class TrainCancellation(Base):
    __tablename__ = "train_cancellations"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), nullable=False, index=True)
    journey_date = Column(Date, nullable=False, index=True)
    cancellation_type = Column(String(30), default="Full") # Full, Partial
    reason = Column(String(200), nullable=True)
    notification_date = Column(DateTime, default=datetime.datetime.utcnow)

# 20. train_diversions
class TrainDiversion(Base):
    __tablename__ = "train_diversions"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), nullable=False, index=True)
    journey_date = Column(Date, nullable=False, index=True)
    diverted_from_station = Column(String(10), nullable=False)
    diverted_to_station = Column(String(10), nullable=False)
    via_stations = Column(JSON, nullable=True)
    reason = Column(String(200), nullable=True)

# 21. train_live_status
class TrainLiveStatus(Base):
    __tablename__ = "train_live_status"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), nullable=False, index=True)
    journey_date = Column(Date, nullable=False, index=True)
    current_station_code = Column(String(10), nullable=True)
    previous_station_code = Column(String(10), nullable=True)
    next_station_code = Column(String(10), nullable=True)
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    speed_kmh = Column(Float, default=0.0)
    delay_minutes = Column(Float, default=0.0)
    status_label = Column(String(50), default="On Time") # Right Time, Delayed by 15m, Arrived
    actual_platform = Column(String(10), default="Not Available")
    estimated_destination_arrival = Column(String(20), nullable=True)
    last_updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    data_source = Column(String(100), default="CRIS / NTES Live Feed")

# 22. station_live_status
class StationLiveStatus(Base):
    __tablename__ = "station_live_status"
    
    id = Column(Integer, primary_key=True, index=True)
    station_code = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    expected_trains_count = Column(Integer, default=0)
    delayed_trains_count = Column(Integer, default=0)
    current_congestion_level = Column(String(30), default="Normal") # Low, Normal, High, Congested
    active_announcements = Column(JSON, nullable=True)

# 23. platform_assignments
class PlatformAssignment(Base):
    __tablename__ = "platform_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), nullable=False, index=True)
    station_code = Column(String(10), nullable=False, index=True)
    platform_number = Column(String(10), nullable=False)
    assignment_type = Column(String(40), default="Scheduled") # Infrastructure, Scheduled, Announced, Live_Confirmed
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    source = Column(String(100), default="Station Working Rules / Verified Timetable")

    __table_args__ = (
        Index("idx_platform_assign", "train_number", "station_code"),
    )

# 24. railway_operational_events
class RailwayOperationalEvent(Base):
    __tablename__ = "railway_operational_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(60), unique=True, index=True, nullable=False)
    event_type = Column(String(50), nullable=False) # Crossing, Overtaking, Being_Overtaken, Junction_Crossing, Direction_Reversal
    station_code = Column(String(10), nullable=False, index=True)
    first_train_number = Column(String(10), nullable=False, index=True)
    first_train_name = Column(String(120), nullable=True)
    second_train_number = Column(String(10), nullable=False, index=True)
    second_train_name = Column(String(120), nullable=True)
    scheduled_time = Column(String(10), nullable=True) # "HH:MM"
    direction_first = Column(String(30), default="Down (Northbound)")
    direction_second = Column(String(30), default="Up (Southbound)")
    track_line = Column(String(50), default="Main Track / Loop Line")
    verification_status = Column(String(50), default="Timetable-Derived Operational Meet") # Timetable-Derived, Confirmed Real-World Event
    confidence_level = Column(Float, default=0.92)

# 25. data_sources
class DataSource(Base):
    __tablename__ = "data_sources"
    
    source_id = Column(String(50), primary_key=True, index=True)
    source_name = Column(String(120), nullable=False)
    dataset_version = Column(String(50), default="2026.1")
    license_info = Column(String(100), default="Government Open Data License - India (GODL) / Open Data")
    coverage_summary = Column(Text, nullable=True)
    record_count = Column(Integer, default=0)
    validation_status = Column(String(40), default="Verified")
    last_synced_at = Column(DateTime, default=datetime.datetime.utcnow)

# 26. dataset_versions
class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    
    version_id = Column(String(60), primary_key=True, index=True)
    source_id = Column(String(50), ForeignKey("data_sources.source_id"), nullable=False)
    version_tag = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)
    checksum = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_current = Column(Boolean, default=True)

# 27. data_import_logs
class DataImportLog(Base):
    __tablename__ = "data_import_logs"
    
    log_id = Column(String(60), primary_key=True, index=True)
    filename = Column(String(150), nullable=False)
    dataset_type = Column(String(50), nullable=False) # Trains, Stations, Timetables, Distances, Maps
    total_imported = Column(Integer, default=0)
    valid_count = Column(Integer, default=0)
    invalid_count = Column(Integer, default=0)
    duplicates_count = Column(Integer, default=0)
    imported_by = Column(String(50), default="System Ingestion Engine")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)

# 28. data_correction_logs
class DataCorrectionLog(Base):
    __tablename__ = "data_correction_logs"
    
    correction_id = Column(String(60), primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False) # Station, Train, Platform, RouteStop
    entity_id = Column(String(50), nullable=False)
    field_name = Column(String(50), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    corrected_by = Column(String(50), default="Administrator")
    reason = Column(Text, nullable=True)
    corrected_at = Column(DateTime, default=datetime.datetime.utcnow)


# ============================================================================
# COMPATIBILITY & ML ANALYTICS TABLES (Preserved for prediction models)
# ============================================================================

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
    weather_condition = Column(String(50), nullable=True)
    congestion_level = Column(String(20), default="Normal")
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
    delay_category = Column(String(30), nullable=False)
    primary_cause_guess = Column(String(100), nullable=True)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)

class ImportedDataset(Base):
    __tablename__ = "imported_datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(120), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_path = Column(String(255), nullable=True)
    total_records = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    invalid_records = Column(Integer, default=0)
    cleaning_summary = Column(JSON, nullable=True)
    status = Column(String(30), default="Pending")
    upload_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, index=True, nullable=False)
    model_type = Column(String(50), nullable=False)
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
    status = Column(String(30), default="Completed")
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
    late_probability = Column(Float, default=0.0)
    delay_category = Column(String(30), nullable=False)
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(30), nullable=True)
    actual_delay_minutes = Column(Float, nullable=True)
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
    role = Column(String(20), default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
