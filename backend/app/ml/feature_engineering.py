import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "previous_station_delay",
    "halt_duration_minutes",
    "distance_km",
    "dep_hour",
    "dep_minute",
    "day_of_week_num",
    "is_weekend",
    "train_category_rank", # Priority rank: Rajdhani/Vande Bharat = 1, Superfast = 2, Mail = 3, Passenger = 4
    "weather_impact_score", # 0: Clear, 1: Rain, 2: Fog
    "congestion_score",     # 0: Low, 1: Normal, 2: High
    "historical_avg_route_delay"
]

CATEGORY_RANK_MAP = {
    "Vande Bharat": 1,
    "Rajdhani": 1,
    "Shatabdi": 1,
    "Tejas": 1,
    "Superfast": 2,
    "Mail/Express": 3,
    "Express": 3,
    "Passenger": 4,
}

WEATHER_SCORE_MAP = {
    "Clear": 0,
    "Light Rain": 0.5,
    "Rain": 1.0,
    "Heavy Rain": 1.5,
    "Fog": 2.0,
    "Dense Fog": 2.5
}

CONGESTION_SCORE_MAP = {
    "Low": 0.0,
    "Normal": 1.0,
    "Medium": 1.5,
    "High": 2.5,
    "Severe": 3.0
}

DAYS_MAP = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6,
    "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6
}

def parse_time_to_hm(time_str: str) -> Tuple[int, int]:
    """Parse 'HH:MM' string to (hour, minute)."""
    if not time_str or not isinstance(time_str, str):
        return 8, 0
    parts = time_str.strip().split(":")
    try:
        h = int(parts[0]) % 24
        m = int(parts[1]) if len(parts) > 1 else 0
        return h, m
    except Exception:
        return 8, 0

def extract_features_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw railway data into model-ready features.
    """
    df_clean = df.copy()
    
    # 1. Previous station delay
    if "previous_station_delay" not in df_clean.columns:
        if "delay_departure_minutes" in df_clean.columns:
            df_clean["previous_station_delay"] = df_clean["delay_departure_minutes"].shift(1).fillna(0.0)
        else:
            df_clean["previous_station_delay"] = 0.0
    else:
        df_clean["previous_station_delay"] = df_clean["previous_station_delay"].fillna(0.0)

    # 2. Halt duration
    if "halt_duration_minutes" not in df_clean.columns:
        df_clean["halt_duration_minutes"] = 2.0
    df_clean["halt_duration_minutes"] = pd.to_numeric(df_clean["halt_duration_minutes"], errors="coerce").fillna(2.0)
    
    # 3. Distance
    if "distance_km" not in df_clean.columns:
        df_clean["distance_km"] = 100.0
    df_clean["distance_km"] = pd.to_numeric(df_clean["distance_km"], errors="coerce").fillna(100.0)
    
    # 4. Departure hour & minute
    dep_col = "scheduled_departure" if "scheduled_departure" in df_clean.columns else "departure_time"
    if dep_col in df_clean.columns:
        dep_parsed = df_clean[dep_col].apply(parse_time_to_hm)
        df_clean["dep_hour"] = [p[0] for p in dep_parsed]
        df_clean["dep_minute"] = [p[1] for p in dep_parsed]
    else:
        df_clean["dep_hour"] = 8
        df_clean["dep_minute"] = 0
        
    # 5. Day of week
    if "day_of_week" in df_clean.columns:
        df_clean["day_of_week_num"] = df_clean["day_of_week"].map(DAYS_MAP).fillna(2)
    elif "journey_date" in df_clean.columns:
        df_clean["day_of_week_num"] = pd.to_datetime(df_clean["journey_date"], errors="coerce").dt.dayofweek.fillna(2)
    else:
        df_clean["day_of_week_num"] = 2
        
    df_clean["is_weekend"] = df_clean["day_of_week_num"].apply(lambda d: 1 if d in [5, 6] else 0)
    
    # 6. Train category rank
    if "train_category" in df_clean.columns:
        df_clean["train_category_rank"] = df_clean["train_category"].map(CATEGORY_RANK_MAP).fillna(3)
    else:
        df_clean["train_category_rank"] = 3
        
    # 7. Weather impact score
    if "weather_condition" in df_clean.columns:
        df_clean["weather_impact_score"] = df_clean["weather_condition"].map(WEATHER_SCORE_MAP).fillna(0.0)
    else:
        df_clean["weather_impact_score"] = 0.0
        
    # 8. Congestion score
    if "congestion_level" in df_clean.columns:
        df_clean["congestion_score"] = df_clean["congestion_level"].map(CONGESTION_SCORE_MAP).fillna(1.0)
    else:
        df_clean["congestion_score"] = 1.0
        
    # 9. Historical route delay feature (moving average / train default)
    if "historical_avg_route_delay" not in df_clean.columns:
        if "delay_arrival_minutes" in df_clean.columns and "train_number" in df_clean.columns:
            train_means = df_clean.groupby("train_number")["delay_arrival_minutes"].transform("mean")
            df_clean["historical_avg_route_delay"] = train_means.fillna(15.0)
        else:
            df_clean["historical_avg_route_delay"] = 15.0
    else:
        df_clean["historical_avg_route_delay"] = pd.to_numeric(
            df_clean["historical_avg_route_delay"], errors="coerce"
        ).fillna(15.0)
        
    return df_clean[FEATURE_COLUMNS]

def chronological_split(
    df: pd.DataFrame, 
    date_col: str = "journey_date", 
    test_size: float = 0.2
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Strict chronological train/test split to prevent temporal data leakage.
    Earlier records belong to the training set; strictly later records form the test set.
    """
    df_sorted = df.sort_values(by=date_col).reset_index(drop=True)
    split_idx = int(len(df_sorted) * (1.0 - test_size))
    train_df = df_sorted.iloc[:split_idx].copy()
    test_df = df_sorted.iloc[split_idx:].copy()
    return train_df, test_df
