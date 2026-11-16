import os
import io
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

from backend.app.core.logging import logger

REQUIRED_MINIMAL_COLUMNS = ["train_number", "station_code", "journey_date"]

RECOMMENDED_COLUMNS = [
    "train_number", "train_name", "station_code",
    "scheduled_arrival", "actual_arrival",
    "scheduled_departure", "actual_departure",
    "delay_arrival_minutes", "delay_departure_minutes",
    "journey_date", "distance_km", "train_category", "day_of_week"
]

class RailwayDataProcessor:
    def __init__(self):
        pass

    def load_file_to_df(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """
        Load CSV, Excel (.xlsx, .xls) or JSON files into a Pandas DataFrame.
        """
        lower_name = filename.lower()
        if lower_name.endswith(".csv"):
            return pd.read_csv(io.BytesIO(file_content))
        elif lower_name.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(file_content))
        elif lower_name.endswith(".json"):
            data = json.loads(file_content.decode("utf-8"))
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # Check for records inside a key like 'data' or 'records'
                for k in ["data", "records", "rows"]:
                    if k in data and isinstance(data[k], list):
                        return pd.DataFrame(data[k])
                return pd.DataFrame([data])
            else:
                raise ValueError("JSON file format not supported: Must be an array or object containing array of records")
        else:
            raise ValueError(f"Unsupported file format for '{filename}'. Expected CSV, Excel (.xlsx/.xls) or JSON.")

    def validate_and_clean_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Perform complete validation, deduplication, missing value imputation,
        outlier handling, and feature enrichment.
        """
        raw_count = len(df)
        cleaning_report = {
            "initial_rows": raw_count,
            "duplicates_removed": 0,
            "missing_values_imputed": 0,
            "outliers_adjusted": 0,
            "invalid_rows_dropped": 0,
            "final_clean_rows": 0,
            "columns_present": list(df.columns)
        }

        # 1. Normalize column names (lowercase, stripped, replace spaces with underscores)
        df_clean = df.copy()
        df_clean.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df_clean.columns]
        
        # 2. Check minimal required columns
        for req in REQUIRED_MINIMAL_COLUMNS:
            if req not in df_clean.columns:
                raise ValueError(f"Missing mandatory column: '{req}'. Data must contain train_number, station_code, and journey_date.")

        # 3. Drop exact duplicates
        before_dedup = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=["train_number", "station_code", "journey_date"]).reset_index(drop=True)
        cleaning_report["duplicates_removed"] = before_dedup - len(df_clean)

        # 4. Standardize train_number and station_code
        df_clean["train_number"] = df_clean["train_number"].astype(str).str.strip()
        df_clean["station_code"] = df_clean["station_code"].astype(str).str.strip().str.upper()

        # Drop invalid rows where station_code or train_number is empty/null
        valid_mask = (df_clean["train_number"] != "") & (df_clean["station_code"] != "") & (df_clean["train_number"] != "nan")
        dropped_invalid = len(df_clean) - valid_mask.sum()
        df_clean = df_clean[valid_mask].copy()
        cleaning_report["invalid_rows_dropped"] += dropped_invalid

        # 5. Parse journey_date
        df_clean["journey_date"] = pd.to_datetime(df_clean["journey_date"], errors="coerce")
        null_dates = df_clean["journey_date"].isna().sum()
        if null_dates > 0:
            df_clean = df_clean.dropna(subset=["journey_date"]).copy()
            cleaning_report["invalid_rows_dropped"] += null_dates
        df_clean["journey_date"] = df_clean["journey_date"].dt.date

        # 6. Distance KM handling
        if "distance_km" in df_clean.columns:
            df_clean["distance_km"] = pd.to_numeric(df_clean["distance_km"], errors="coerce").fillna(50.0)
        elif "distance" in df_clean.columns:
            df_clean["distance_km"] = pd.to_numeric(df_clean["distance"], errors="coerce").fillna(50.0)
        else:
            df_clean["distance_km"] = 50.0
            cleaning_report["missing_values_imputed"] += len(df_clean)
        df_clean.loc[df_clean["distance_km"] < 0, "distance_km"] = 0.0

        # 7. Delay columns calculation and outlier trimming
        # Outlier rule: delay cannot be < -30 mins or > 1440 mins (24 hours) for normal running records
        for d_col in ["delay_arrival_minutes", "delay_departure_minutes", "delay_minutes", "delay"]:
            if d_col in df_clean.columns:
                df_clean[d_col] = pd.to_numeric(df_clean[d_col], errors="coerce").fillna(0.0)
                outliers = (df_clean[d_col] < -30.0) | (df_clean[d_col] > 1440.0)
                if outliers.sum() > 0:
                    df_clean.loc[df_clean[d_col] < -30.0, d_col] = -10.0
                    df_clean.loc[df_clean[d_col] > 1440.0, d_col] = 720.0
                    cleaning_report["outliers_adjusted"] += int(outliers.sum())

        if "delay_arrival_minutes" not in df_clean.columns:
            if "delay_minutes" in df_clean.columns:
                df_clean["delay_arrival_minutes"] = df_clean["delay_minutes"]
            elif "delay" in df_clean.columns:
                df_clean["delay_arrival_minutes"] = df_clean["delay"]
            else:
                df_clean["delay_arrival_minutes"] = 0.0
                cleaning_report["missing_values_imputed"] += len(df_clean)

        if "delay_departure_minutes" not in df_clean.columns:
            df_clean["delay_departure_minutes"] = df_clean["delay_arrival_minutes"]

        # 8. Train category & day of week
        if "train_category" not in df_clean.columns:
            df_clean["train_category"] = "Express"
        else:
            df_clean["train_category"] = df_clean["train_category"].fillna("Express").astype(str)

        if "day_of_week" not in df_clean.columns:
            df_clean["day_of_week"] = pd.to_datetime(df_clean["journey_date"]).dt.day_name()

        # 9. Halt duration
        if "halt_duration_minutes" not in df_clean.columns:
            df_clean["halt_duration_minutes"] = 2.0

        cleaning_report["final_clean_rows"] = len(df_clean)
        logger.info(f"Data validation complete: {cleaning_report}")
        return df_clean, cleaning_report
