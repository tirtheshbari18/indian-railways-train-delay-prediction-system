import os
import json
import random
import datetime
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.security import get_password_hash
from backend.app.models.schema import (
    Station, Train, TrainRoute, HistoricalTrainRunning,
    DelayRecord, ImportedDataset, User
)

STATIONS_DATA = [
    {"station_code": "NDLS", "station_name": "New Delhi", "zone": "NR", "state": "Delhi", "division": "Delhi", "latitude": 28.6415, "longitude": 77.2198},
    {"station_code": "MMCT", "station_name": "Mumbai Central", "zone": "WR", "state": "Maharashtra", "division": "Mumbai", "latitude": 18.9696, "longitude": 72.8194},
    {"station_code": "CSMT", "station_name": "Mumbai CSMT", "zone": "CR", "state": "Maharashtra", "division": "Mumbai", "latitude": 18.9402, "longitude": 72.8356},
    {"station_code": "HWH", "station_name": "Howrah Junction", "zone": "ER", "state": "West Bengal", "division": "Howrah", "latitude": 22.5840, "longitude": 88.3426},
    {"station_code": "MAS", "station_name": "Chennai Central", "zone": "SR", "state": "Tamil Nadu", "division": "Chennai", "latitude": 13.0827, "longitude": 80.2707},
    {"station_code": "SBC", "station_name": "KSR Bengaluru", "zone": "SWR", "state": "Karnataka", "division": "Bengaluru", "latitude": 12.9784, "longitude": 77.5684},
    {"station_code": "CNB", "station_name": "Kanpur Central", "zone": "NCR", "state": "Uttar Pradesh", "division": "Prayagraj", "latitude": 26.4547, "longitude": 80.3507},
    {"station_code": "PRYJ", "station_name": "Prayagraj Junction", "zone": "NCR", "state": "Uttar Pradesh", "division": "Prayagraj", "latitude": 25.4484, "longitude": 81.8333},
    {"station_code": "DDU", "station_name": "Pt. Deen Dayal Upadhyaya Jn", "zone": "ECR", "state": "Uttar Pradesh", "division": "DDU", "latitude": 25.2818, "longitude": 83.1197},
    {"station_code": "BSB", "station_name": "Varanasi Junction", "zone": "NR", "state": "Uttar Pradesh", "division": "Varanasi", "latitude": 25.3276, "longitude": 82.9866},
    {"station_code": "LKO", "station_name": "Lucknow Charbagh", "zone": "NR", "state": "Uttar Pradesh", "division": "Lucknow", "latitude": 26.8322, "longitude": 80.9234},
    {"station_code": "KOTA", "station_name": "Kota Junction", "zone": "WCR", "state": "Rajasthan", "division": "Kota", "latitude": 25.2238, "longitude": 75.8648},
    {"station_code": "BRC", "station_name": "Vadodara Junction", "zone": "WR", "state": "Gujarat", "division": "Vadodara", "latitude": 22.3107, "longitude": 73.1812},
    {"station_code": "ST", "station_name": "Surat", "zone": "WR", "state": "Gujarat", "division": "Mumbai", "latitude": 21.2050, "longitude": 72.8407},
    {"station_code": "BVI", "station_name": "Borivali", "zone": "WR", "state": "Maharashtra", "division": "Mumbai", "latitude": 19.2290, "longitude": 72.8570},
    {"station_code": "RTM", "station_name": "Ratlam Junction", "zone": "WR", "state": "Madhya Pradesh", "division": "Ratlam", "latitude": 23.3441, "longitude": 75.0374},
    {"station_code": "GWL", "station_name": "Gwalior Junction", "zone": "NCR", "state": "Madhya Pradesh", "division": "Jhansi", "latitude": 26.2183, "longitude": 78.1828},
    {"station_code": "VGLJ", "station_name": "VGL Jhansi Junction", "zone": "NCR", "state": "Uttar Pradesh", "division": "Jhansi", "latitude": 25.4484, "longitude": 78.5685},
    {"station_code": "BPL", "station_name": "Bhopal Junction", "zone": "WCR", "state": "Madhya Pradesh", "division": "Bhopal", "latitude": 23.2662, "longitude": 77.4126},
    {"station_code": "ET", "station_name": "Itarsi Junction", "zone": "WCR", "state": "Madhya Pradesh", "division": "Bhopal", "latitude": 22.6122, "longitude": 77.7641},
    {"station_code": "NGP", "station_name": "Nagpur Junction", "zone": "CR", "state": "Maharashtra", "division": "Nagpur", "latitude": 21.1524, "longitude": 79.0888},
    {"station_code": "BZA", "station_name": "Vijayawada Junction", "zone": "SCR", "state": "Andhra Pradesh", "division": "Vijayawada", "latitude": 16.5186, "longitude": 80.6200},
    {"station_code": "GAYA", "station_name": "Gaya Junction", "zone": "ECR", "state": "Bihar", "division": "DDU", "latitude": 24.8020, "longitude": 85.0064},
    {"station_code": "DHN", "station_name": "Dhanbad Junction", "zone": "ECR", "state": "Jharkhand", "division": "Dhanbad", "latitude": 23.7957, "longitude": 86.4304},
    {"station_code": "AGC", "station_name": "Agra Cantt", "zone": "NCR", "state": "Uttar Pradesh", "division": "Agra", "latitude": 27.1592, "longitude": 77.9904},
]

TRAINS_DATA = [
    {
        "train_number": "12951",
        "train_name": "Mumbai Tejas Rajdhani Express",
        "train_category": "Rajdhani",
        "source_station_code": "MMCT",
        "dest_station_code": "NDLS",
        "total_distance_km": 1386.0,
        "runs_on_days": "Daily",
        "route": [
            {"station_code": "MMCT", "stop_number": 1, "arr": "17:00", "dep": "17:00", "halt": 0, "km": 0},
            {"station_code": "BVI", "stop_number": 2, "arr": "17:22", "dep": "17:24", "halt": 2, "km": 30},
            {"station_code": "ST", "stop_number": 3, "arr": "19:43", "dep": "19:48", "halt": 5, "km": 263},
            {"station_code": "BRC", "stop_number": 4, "arr": "21:06", "dep": "21:16", "halt": 10, "km": 392},
            {"station_code": "RTM", "stop_number": 5, "arr": "00:25", "dep": "00:28", "halt": 3, "km": 653},
            {"station_code": "KOTA", "stop_number": 6, "arr": "03:15", "dep": "03:20", "halt": 5, "km": 920},
            {"station_code": "NDLS", "stop_number": 7, "arr": "08:32", "dep": "08:32", "halt": 0, "km": 1386},
        ]
    },
    {
        "train_number": "12952",
        "train_name": "New Delhi - Mumbai Tejas Rajdhani",
        "train_category": "Rajdhani",
        "source_station_code": "NDLS",
        "dest_station_code": "MMCT",
        "total_distance_km": 1386.0,
        "runs_on_days": "Daily",
        "route": [
            {"station_code": "NDLS", "stop_number": 1, "arr": "16:55", "dep": "16:55", "halt": 0, "km": 0},
            {"station_code": "KOTA", "stop_number": 2, "arr": "21:30", "dep": "21:40", "halt": 10, "km": 466},
            {"station_code": "RTM", "stop_number": 3, "arr": "00:35", "dep": "00:38", "halt": 3, "km": 733},
            {"station_code": "BRC", "stop_number": 4, "arr": "03:45", "dep": "03:55", "halt": 10, "km": 994},
            {"station_code": "ST", "stop_number": 5, "arr": "05:13", "dep": "05:18", "halt": 5, "km": 1123},
            {"station_code": "BVI", "stop_number": 6, "arr": "07:35", "dep": "07:37", "halt": 2, "km": 1356},
            {"station_code": "MMCT", "stop_number": 7, "arr": "08:35", "dep": "08:35", "halt": 0, "km": 1386},
        ]
    },
    {
        "train_number": "22436",
        "train_name": "New Delhi - Varanasi Vande Bharat Express",
        "train_category": "Vande Bharat",
        "source_station_code": "NDLS",
        "dest_station_code": "BSB",
        "total_distance_km": 759.0,
        "runs_on_days": "Tue,Wed,Fri,Sat,Sun",
        "route": [
            {"station_code": "NDLS", "stop_number": 1, "arr": "06:00", "dep": "06:00", "halt": 0, "km": 0},
            {"station_code": "CNB", "stop_number": 2, "arr": "10:08", "dep": "10:10", "halt": 2, "km": 441},
            {"station_code": "PRYJ", "stop_number": 3, "arr": "12:08", "dep": "12:10", "halt": 2, "km": 635},
            {"station_code": "BSB", "stop_number": 4, "arr": "14:00", "dep": "14:00", "halt": 0, "km": 759},
        ]
    },
    {
        "train_number": "22435",
        "train_name": "Varanasi - New Delhi Vande Bharat Express",
        "train_category": "Vande Bharat",
        "source_station_code": "BSB",
        "dest_station_code": "NDLS",
        "total_distance_km": 759.0,
        "runs_on_days": "Tue,Wed,Fri,Sat,Sun",
        "route": [
            {"station_code": "BSB", "stop_number": 1, "arr": "15:00", "dep": "15:00", "halt": 0, "km": 0},
            {"station_code": "PRYJ", "stop_number": 2, "arr": "16:30", "dep": "16:32", "halt": 2, "km": 124},
            {"station_code": "CNB", "stop_number": 3, "arr": "18:30", "dep": "18:32", "halt": 2, "km": 318},
            {"station_code": "NDLS", "stop_number": 4, "arr": "23:00", "dep": "23:00", "halt": 0, "km": 759},
        ]
    },
    {
        "train_number": "12004",
        "train_name": "Lucknow Swarna Shatabdi Express",
        "train_category": "Shatabdi",
        "source_station_code": "NDLS",
        "dest_station_code": "LKO",
        "total_distance_km": 512.0,
        "runs_on_days": "Daily",
        "route": [
            {"station_code": "NDLS", "stop_number": 1, "arr": "06:10", "dep": "06:10", "halt": 0, "km": 0},
            {"station_code": "CNB", "stop_number": 2, "arr": "11:20", "dep": "11:25", "halt": 5, "km": 435},
            {"station_code": "LKO", "stop_number": 3, "arr": "12:55", "dep": "12:55", "halt": 0, "km": 512},
        ]
    },
    {
        "train_number": "12301",
        "train_name": "Howrah - New Delhi Rajdhani Express (via Gaya)",
        "train_category": "Rajdhani",
        "source_station_code": "HWH",
        "dest_station_code": "NDLS",
        "total_distance_km": 1451.0,
        "runs_on_days": "Mon,Tue,Wed,Thu,Sat,Sun",
        "route": [
            {"station_code": "HWH", "stop_number": 1, "arr": "16:50", "dep": "16:50", "halt": 0, "km": 0},
            {"station_code": "DHN", "stop_number": 2, "arr": "19:55", "dep": "20:00", "halt": 5, "km": 259},
            {"station_code": "GAYA", "stop_number": 3, "arr": "22:19", "dep": "22:22", "halt": 3, "km": 458},
            {"station_code": "DDU", "stop_number": 4, "arr": "00:45", "dep": "00:55", "halt": 10, "km": 663},
            {"station_code": "PRYJ", "stop_number": 5, "arr": "02:43", "dep": "02:45", "halt": 2, "km": 816},
            {"station_code": "CNB", "stop_number": 6, "arr": "04:50", "dep": "04:55", "halt": 5, "km": 1010},
            {"station_code": "NDLS", "stop_number": 7, "arr": "10:05", "dep": "10:05", "halt": 0, "km": 1451},
        ]
    },
    {
        "train_number": "12621",
        "train_name": "Tamil Nadu Express",
        "train_category": "Superfast",
        "source_station_code": "MAS",
        "dest_station_code": "NDLS",
        "total_distance_km": 2182.0,
        "runs_on_days": "Daily",
        "route": [
            {"station_code": "MAS", "stop_number": 1, "arr": "22:00", "dep": "22:00", "halt": 0, "km": 0},
            {"station_code": "BZA", "stop_number": 2, "arr": "03:55", "dep": "04:05", "halt": 10, "km": 431},
            {"station_code": "NGP", "stop_number": 3, "arr": "13:50", "dep": "13:55", "halt": 5, "km": 1094},
            {"station_code": "ET", "stop_number": 4, "arr": "18:30", "dep": "18:35", "halt": 5, "km": 1392},
            {"station_code": "BPL", "stop_number": 5, "arr": "20:10", "dep": "20:20", "halt": 10, "km": 1484},
            {"station_code": "VGLJ", "stop_number": 6, "arr": "00:25", "dep": "00:33", "halt": 8, "km": 1776},
            {"station_code": "GWL", "stop_number": 7, "arr": "01:43", "dep": "01:45", "halt": 2, "km": 1874},
            {"station_code": "AGC", "stop_number": 8, "arr": "03:15", "dep": "03:17", "halt": 2, "km": 1992},
            {"station_code": "NDLS", "stop_number": 9, "arr": "06:30", "dep": "06:30", "halt": 0, "km": 2182},
        ]
    },
    {
        "train_number": "12810",
        "train_name": "Howrah - Mumbai CSMT Mail",
        "train_category": "Superfast",
        "source_station_code": "HWH",
        "dest_station_code": "CSMT",
        "total_distance_km": 1968.0,
        "runs_on_days": "Daily",
        "route": [
            {"station_code": "HWH", "stop_number": 1, "arr": "20:05", "dep": "20:05", "halt": 0, "km": 0},
            {"station_code": "NGP", "stop_number": 2, "arr": "13:55", "dep": "14:00", "halt": 5, "km": 1131},
            {"station_code": "CSMT", "stop_number": 3, "arr": "04:25", "dep": "04:25", "halt": 0, "km": 1968},
        ]
    },
    {
        "train_number": "12627",
        "train_name": "Karnataka Express",
        "train_category": "Superfast",
        "source_station_code": "SBC",
        "dest_station_code": "NDLS",
        "total_distance_km": 2406.0,
        "runs_on_days": "Daily",
        "route": [
            {"station_code": "SBC", "stop_number": 1, "arr": "19:20", "dep": "19:20", "halt": 0, "km": 0},
            {"station_code": "ET", "stop_number": 2, "arr": "22:50", "dep": "23:00", "halt": 10, "km": 1614},
            {"station_code": "BPL", "stop_number": 3, "arr": "00:45", "dep": "00:50", "halt": 5, "km": 1706},
            {"station_code": "VGLJ", "stop_number": 4, "arr": "04:45", "dep": "04:53", "halt": 8, "km": 1998},
            {"station_code": "AGC", "stop_number": 5, "arr": "07:50", "dep": "07:55", "halt": 5, "km": 2214},
            {"station_code": "NDLS", "stop_number": 6, "arr": "10:30", "dep": "10:30", "halt": 0, "km": 2406},
        ]
    },
    {
        "train_number": "12779",
        "train_name": "Goa Express",
        "train_category": "Express",
        "source_station_code": "MMCT",
        "dest_station_code": "NDLS",
        "total_distance_km": 1820.0,
        "runs_on_days": "Daily",
        "route": [
            {"station_code": "MMCT", "stop_number": 1, "arr": "15:00", "dep": "15:00", "halt": 0, "km": 0},
            {"station_code": "ST", "stop_number": 2, "arr": "19:00", "dep": "19:05", "halt": 5, "km": 263},
            {"station_code": "ET", "stop_number": 3, "arr": "06:10", "dep": "06:20", "halt": 10, "km": 1010},
            {"station_code": "BPL", "stop_number": 4, "arr": "08:15", "dep": "08:20", "halt": 5, "km": 1102},
            {"station_code": "VGLJ", "stop_number": 5, "arr": "12:50", "dep": "12:58", "halt": 8, "km": 1394},
            {"station_code": "AGC", "stop_number": 6, "arr": "16:15", "dep": "16:20", "halt": 5, "km": 1610},
            {"station_code": "NDLS", "stop_number": 7, "arr": "19:40", "dep": "19:40", "halt": 0, "km": 1820},
        ]
    }
]

def generate_historical_dataset(db: Session, num_days: int = 120) -> pd.DataFrame:
    """
    Generate realistic historical railway operations dataset over chronologically ordered dates.
    Models real Indian railway phenomena:
    - Winter Fog in NCR/Northern Railway (NDLS, CNB, PRYJ, DDU) during Dec-Jan
    - Freight crossing bottleneck around Kanpur & Mughal Sarai
    - Train category priority (Rajdhani/Vande Bharat prioritized over Express)
    - Compounding delays downstream
    """
    records = []
    # Dates spanning 120 days up to recent
    base_date = datetime.date(2026, 7, 15)
    
    random.seed(42)
    np.random.seed(42)

    for day_idx in range(num_days):
        current_date = base_date + datetime.timedelta(days=day_idx)
        month = current_date.month
        day_of_week = current_date.strftime("%A")
        
        # Weather condition based on month/season
        is_winter = month in [12, 1, 2]
        is_monsoon = month in [7, 8]
        
        for t_info in TRAINS_DATA:
            t_num = t_info["train_number"]
            t_name = t_info["train_name"]
            t_cat = t_info["train_category"]
            route = t_info["route"]
            
            # Category baseline delay factor
            cat_factor = 0.5 if t_cat == "Vande Bharat" else (0.6 if t_cat == "Rajdhani" else (0.8 if t_cat == "Shatabdi" else 1.3))
            
            # Start of trip delay (initial departure lag)
            current_delay = 0.0
            if random.random() < 0.25:
                current_delay = random.uniform(5.0, 30.0) * cat_factor
                
            for stop in route:
                st_code = stop["station_code"]
                dist = stop["km"]
                halt = stop["halt"]
                arr_time = stop["arr"]
                dep_time = stop["dep"]
                
                # Weather at this station
                weather = "Clear"
                if is_winter and st_code in ["NDLS", "CNB", "PRYJ", "DDU", "BSB", "AGC", "GWL"]:
                    weather = "Fog" if random.random() < 0.6 else "Dense Fog"
                elif is_monsoon and random.random() < 0.4:
                    weather = "Rain"
                    
                # Section Congestion
                congestion = "Normal"
                if st_code in ["CNB", "DDU", "ET", "BPL", "NDLS"]:
                    congestion = "High" if random.random() < 0.5 else "Normal"
                    
                # Dynamic delay change across segments
                weather_add = 0.0
                if weather == "Dense Fog":
                    weather_add = random.uniform(15.0, 45.0)
                elif weather == "Fog":
                    weather_add = random.uniform(8.0, 25.0)
                elif weather == "Rain":
                    weather_add = random.uniform(5.0, 15.0)
                    
                congestion_add = 0.0
                if congestion == "High":
                    congestion_add = random.uniform(8.0, 20.0) * cat_factor
                    
                # Slack recovery: trains can make up 5-15 mins on long stretches if speed permits
                slack_recovery = 0.0
                if current_delay > 15.0 and dist > 300 and weather == "Clear":
                    slack_recovery = random.uniform(5.0, 15.0) / cat_factor
                    
                segment_variation = random.gauss(1.0, 4.0) * cat_factor
                
                # Calculate arrival delay
                arrival_delay = max(-5.0, current_delay + weather_add + congestion_add - slack_recovery + segment_variation)
                arrival_delay = round(arrival_delay, 1)
                
                # Departure delay includes halt extension if crowded
                dep_extension = random.uniform(0.0, 3.0) if congestion == "High" else 0.0
                departure_delay = round(max(arrival_delay, arrival_delay + dep_extension), 1)
                
                # Carry delay to next stop
                current_delay = departure_delay

                records.append({
                    "train_number": t_num,
                    "train_name": t_name,
                    "journey_date": current_date,
                    "station_code": st_code,
                    "scheduled_arrival": arr_time,
                    "actual_arrival": arr_time, # Will format if needed
                    "scheduled_departure": dep_time,
                    "actual_departure": dep_time,
                    "delay_arrival_minutes": arrival_delay,
                    "delay_departure_minutes": departure_delay,
                    "distance_km": float(dist),
                    "halt_duration_minutes": float(halt),
                    "day_of_week": day_of_week,
                    "train_category": t_cat,
                    "weather_condition": weather,
                    "congestion_level": congestion,
                })

    df = pd.DataFrame(records)
    logger.info(f"Generated {len(df)} synthetic historical operational delay records.")
    return df

def seed_database(db: Session, force: bool = False):
    """
    Initialize database schema, populate standard stations, train routes,
    and seed historical dataset if empty.
    """
    # 1. Seed default users
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@indianrailways.gov.in",
            hashed_password=get_password_hash("admin123"),
            full_name="Chief Railway Controller",
            role="admin",
            is_active=True
        )
        analyst_user = User(
            username="analyst",
            email="analyst@indianrailways.gov.in",
            hashed_password=get_password_hash("analyst123"),
            full_name="Senior Data Analyst",
            role="analyst",
            is_active=True
        )
        viewer_user = User(
            username="viewer",
            email="passenger@indianrailways.gov.in",
            hashed_password=get_password_hash("viewer123"),
            full_name="Passenger / General Viewer",
            role="viewer",
            is_active=True
        )
        db.add_all([admin_user, analyst_user, viewer_user])
        db.commit()
        logger.info("Default users created: admin, analyst, viewer")

    # 2. Seed Stations
    existing_stations = db.query(Station).count()
    if existing_stations == 0 or force:
        for st in STATIONS_DATA:
            existing = db.query(Station).filter(Station.station_code == st["station_code"]).first()
            if not existing:
                station_obj = Station(**st)
                db.add(station_obj)
        db.commit()
        logger.info(f"Seeded {len(STATIONS_DATA)} railway stations.")
        
        # Save stations JSON file for easy reference
        stations_json_path = settings.DATA_PATH / "sample_railway_stations.json"
        with open(stations_json_path, "w", encoding="utf-8") as f:
            json.dump(STATIONS_DATA, f, indent=2)

    # 3. Seed Trains & Routes
    existing_trains = db.query(Train).count()
    if existing_trains == 0 or force:
        for t_info in TRAINS_DATA:
            t_num = t_info["train_number"]
            existing = db.query(Train).filter(Train.train_number == t_num).first()
            if not existing:
                train_obj = Train(
                    train_number=t_num,
                    train_name=t_info["train_name"],
                    train_category=t_info["train_category"],
                    source_station_code=t_info["source_station_code"],
                    dest_station_code=t_info["dest_station_code"],
                    total_distance_km=t_info["total_distance_km"],
                    runs_on_days=t_info["runs_on_days"],
                    active=True
                )
                db.add(train_obj)
                db.flush()
                
                for stop in t_info["route"]:
                    route_stop = TrainRoute(
                        train_number=t_num,
                        station_code=stop["station_code"],
                        stop_number=stop["stop_number"],
                        scheduled_arrival=stop["arr"],
                        scheduled_departure=stop["dep"],
                        halt_minutes=float(stop["halt"]),
                        distance_from_source_km=float(stop["km"]),
                        day_offset=1
                    )
                    db.add(route_stop)
        db.commit()
        logger.info(f"Seeded {len(TRAINS_DATA)} trains and their intermediate route stops.")

    # 4. Seed Historical Running Data & Delay Records
    existing_records = db.query(HistoricalTrainRunning).count()
    if existing_records == 0 or force:
        logger.info("Generating realistic historical operational dataset...")
        df_history = generate_historical_dataset(db, num_days=100)
        
        # Save CSV copy to data/
        csv_path = settings.DATA_PATH / "sample_indian_railways_historical_delays.csv"
        df_history.to_csv(csv_path, index=False)
        logger.info(f"Saved sample historical operational dataset to {csv_path}")

        # Insert records into DB in batches
        running_objects = []
        delay_objects = []
        
        for _, row in df_history.iterrows():
            arr_delay = float(row["delay_arrival_minutes"])
            category = "On-Time (0-15m)"
            if arr_delay > 120:
                category = "Severe Delay (>120m)"
            elif arr_delay > 45:
                category = "Moderate Delay (45-120m)"
            elif arr_delay > 15:
                category = "Slight Delay (15-45m)"
                
            rec = HistoricalTrainRunning(
                train_number=str(row["train_number"]),
                train_name=str(row["train_name"]),
                journey_date=row["journey_date"],
                station_code=str(row["station_code"]),
                scheduled_arrival=str(row["scheduled_arrival"]),
                actual_arrival=str(row["actual_arrival"]),
                scheduled_departure=str(row["scheduled_departure"]),
                actual_departure=str(row["actual_departure"]),
                delay_arrival_minutes=arr_delay,
                delay_departure_minutes=float(row["delay_departure_minutes"]),
                distance_km=float(row["distance_km"]),
                halt_duration_minutes=float(row["halt_duration_minutes"]),
                day_of_week=str(row["day_of_week"]),
                train_category=str(row["train_category"]),
                weather_condition=str(row["weather_condition"]),
                congestion_level=str(row["congestion_level"])
            )
            running_objects.append(rec)
            
            d_rec = DelayRecord(
                train_number=str(row["train_number"]),
                journey_date=row["journey_date"],
                station_code=str(row["station_code"]),
                delay_minutes=arr_delay,
                delay_category=category,
                primary_cause_guess=row["weather_condition"] if row["weather_condition"] != "Clear" else (
                    "Junction Congestion" if row["congestion_level"] == "High" else "Normal Running"
                )
            )
            delay_objects.append(d_rec)

        db.bulk_save_objects(running_objects)
        db.bulk_save_objects(delay_objects)

        # Record dataset import
        imported = ImportedDataset(
            dataset_name="Indian_Railways_Operational_History_2026.csv",
            file_type="csv",
            file_path=str(csv_path),
            total_records=len(df_history),
            valid_records=len(df_history),
            invalid_records=0,
            cleaning_summary={"nulls_imputed": 0, "outliers_adjusted": 0, "status": "Clean Operational Benchmark"},
            status="Ready",
            notes="Comprehensive benchmark dataset featuring premier and express corridors across Northern, Western, and Central Railway zones."
        )
        db.add(imported)
        db.commit()
        logger.info(f"Seeded {len(running_objects)} historical operational records into database.")
        return df_history
    else:
        logger.info(f"Database already contains {existing_records} historical records.")
        return None
