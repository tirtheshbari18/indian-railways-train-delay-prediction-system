import pytest
import pandas as pd
import json
from backend.app.services.data_processor import RailwayDataProcessor

def test_validate_and_clean_data():
    processor = RailwayDataProcessor()
    
    # Raw dirty DataFrame
    dirty_data = {
        "Train Number": ["12951", "12951", "22436", "12004", "INVALID"],
        "Station Code": ["NDLS", "NDLS", "CNB", "LKO", ""],
        "Journey Date": ["2026-10-01", "2026-10-01", "2026-10-02", "not-a-date", "2026-10-03"],
        "Delay Minutes": [12.0, 12.0, 2500.0, 10.0, -100.0], # Outliers (>1440 and <-30)
        "Distance": [100, 100, -50, 450, 200]
    }
    df_raw = pd.DataFrame(dirty_data)
    
    clean_df, report = processor.validate_and_clean_data(df_raw)
    
    # 1. Duplicates removed (first two rows are identical train, station, date)
    assert report["duplicates_removed"] >= 1
    # 2. Invalid dates and empty station codes dropped
    assert report["invalid_rows_dropped"] >= 2
    # 3. Outlier delay capped
    assert clean_df["delay_arrival_minutes"].max() <= 720.0
    # 4. Negative distance corrected
    assert clean_df["distance_km"].min() >= 0.0

def test_json_file_loading():
    processor = RailwayDataProcessor()
    sample_records = [
        {"train_number": "12951", "station_code": "MMCT", "journey_date": "2026-09-01", "delay_minutes": 5},
        {"train_number": "12951", "station_code": "BVI", "journey_date": "2026-09-01", "delay_minutes": 8}
    ]
    json_bytes = json.dumps(sample_records).encode("utf-8")
    df = processor.load_file_to_df(json_bytes, "test.json")
    
    assert len(df) == 2
    assert "train_number" in df.columns
