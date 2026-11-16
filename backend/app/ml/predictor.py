import os
import joblib
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from scipy.stats import norm

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.ml.feature_engineering import (
    FEATURE_COLUMNS,
    extract_features_from_df,
    CATEGORY_RANK_MAP,
    WEATHER_SCORE_MAP,
    CONGESTION_SCORE_MAP,
    parse_time_to_hm
)

class TrainDelayPredictor:
    def __init__(self, model_name: Optional[str] = None):
        self.artifacts_dir = settings.MODEL_ARTIFACTS_PATH
        self.model_name = model_name or "xgboost_v1"
        self.model_bundle = None
        self.scaler = None
        self._load_artifacts()

    def _load_artifacts(self):
        # 1. Load scaler
        scaler_path = os.path.join(self.artifacts_dir, "standard_scaler.joblib")
        if os.path.exists(scaler_path):
            try:
                self.scaler = joblib.load(scaler_path)
            except Exception as e:
                logger.warning(f"Failed to load scaler from {scaler_path}: {e}")

        # 2. Try loading specific model bundle
        possible_filenames = [
            f"{self.model_name}.joblib",
            "xgboost_v1.joblib",
            "gradientboosting_v1.joblib",
            "randomforest_v1.joblib",
            "linearregression_v1.joblib"
        ]
        
        for fname in possible_filenames:
            candidate_path = os.path.join(self.artifacts_dir, fname)
            if os.path.exists(candidate_path):
                try:
                    self.model_bundle = joblib.load(candidate_path)
                    self.model_name = fname.replace(".joblib", "")
                    logger.info(f"Loaded trained ML model artifact: {fname} (Type: {self.model_bundle.get('model_type')})")
                    break
                except Exception as e:
                    logger.warning(f"Could not load artifact {candidate_path}: {e}")

    def is_ready(self) -> bool:
        return self.model_bundle is not None and "model" in self.model_bundle and self.scaler is not None

    def get_delay_category(self, delay_minutes: float) -> str:
        if delay_minutes <= 15.0:
            return "On-Time (0-15m)"
        elif delay_minutes <= 45.0:
            return "Slight Delay (15-45m)"
        elif delay_minutes <= 120.0:
            return "Moderate Delay (45-120m)"
        else:
            return "Severe Delay (>120m)"

    def calculate_expected_arrival(self, scheduled_arrival: str, delay_minutes: float) -> str:
        """
        Calculate expected arrival time string 'HH:MM' given scheduled 'HH:MM' and delay.
        """
        try:
            h, m = parse_time_to_hm(scheduled_arrival)
            base_time = datetime(2026, 1, 1, h, m)
            actual_time = base_time + timedelta(minutes=float(delay_minutes))
            return actual_time.strftime("%H:%M")
        except Exception:
            return scheduled_arrival or "12:00"

    def predict_delay(
        self,
        train_number: str,
        train_category: str,
        distance_km: float,
        scheduled_departure: str,
        scheduled_arrival: str,
        journey_date: str,
        previous_station_delay: float = 0.0,
        halt_duration_minutes: float = 2.0,
        weather_condition: str = "Clear",
        congestion_level: str = "Normal",
        historical_avg_route_delay: float = 15.0
    ) -> Dict[str, Any]:
        """
        Produce a real ML-based prediction with uncertainty intervals and explanations.
        """
        # Form single-row DataFrame for feature extraction
        row_dict = {
            "train_number": train_number,
            "train_category": train_category or "Express",
            "distance_km": float(distance_km or 150.0),
            "scheduled_departure": scheduled_departure or "08:00",
            "scheduled_arrival": scheduled_arrival or "14:00",
            "journey_date": str(journey_date),
            "previous_station_delay": float(previous_station_delay or 0.0),
            "halt_duration_minutes": float(halt_duration_minutes or 2.0),
            "weather_condition": weather_condition or "Clear",
            "congestion_level": congestion_level or "Normal",
            "historical_avg_route_delay": float(historical_avg_route_delay or 15.0)
        }
        
        input_df = pd.DataFrame([row_dict])
        raw_features = extract_features_from_df(input_df)
        
        if self.is_ready():
            # Scaled transformation
            scaled_features = self.scaler.transform(raw_features)
            model = self.model_bundle["model"]
            raw_prediction = float(model.predict(scaled_features)[0])
            
            # Retrieve test RMSE from bundle for confidence intervals
            model_metrics = self.model_bundle.get("metrics", {})
            rmse = model_metrics.get("rmse", 14.5)
            model_type = self.model_bundle.get("model_type", "GradientBoosting")
            model_ver = "v1.0"
        else:
            # Baseline domain heuristic fallback if no trained model artifact exists yet
            prev_delay = float(previous_station_delay or 0.0)
            weather_mult = 1.0 + (WEATHER_SCORE_MAP.get(weather_condition, 0.0) * 0.4)
            cong_mult = 1.0 + (CONGESTION_SCORE_MAP.get(congestion_level, 1.0) * 0.15)
            prio = CATEGORY_RANK_MAP.get(train_category, 3)
            prio_mult = 0.7 if prio == 1 else (0.9 if prio == 2 else 1.1)
            
            raw_prediction = (prev_delay * 0.75 + (distance_km / 100.0) * 2.5) * weather_mult * cong_mult * prio_mult
            rmse = 18.0
            model_type = "BaselineStatisticalEstimator"
            model_ver = "v0.1-pretrain"

        # Minimum delay can be 0 or slightly negative (arriving up to 5 min early)
        predicted_delay = round(max(-5.0, min(raw_prediction, 600.0)), 1)
        
        # Calculate 90% confidence interval (z = 1.645)
        half_width = 1.645 * rmse
        lower_bound = round(max(0.0, predicted_delay - half_width), 1)
        upper_bound = round(predicted_delay + half_width, 1)
        
        # Late probability: P(Delay > 15 mins) using normal CDF
        # Z = (15 - predicted_delay) / rmse
        z_score = (15.0 - predicted_delay) / max(rmse, 1.0)
        prob_late = round(float(1.0 - norm.cdf(z_score)), 3)
        prob_late = max(0.01, min(0.99, prob_late))
        
        category = self.get_delay_category(predicted_delay)
        expected_arrival = self.calculate_expected_arrival(scheduled_arrival, predicted_delay)
        
        # Explanatory insights
        explanations = []
        if previous_station_delay > 20:
            explanations.append(f"Significant initial delay ({previous_station_delay}m) carries downstream momentum.")
        elif previous_station_delay == 0:
            explanations.append("Train started on-time from previous checkpoint.")
            
        if weather_condition in ["Fog", "Dense Fog"]:
            explanations.append("Severe winter fog warning: Speed restrictions (60-75 km/h) active on this corridor.")
        elif weather_condition in ["Rain", "Heavy Rain"]:
            explanations.append("Monsoon precipitation causing track caution and signal speed slowdowns.")
            
        if congestion_level in ["High", "Severe"]:
            explanations.append("Section operates above 130% line capacity utilization with heavy freight crossings.")
            
        if train_category in ["Rajdhani", "Vande Bharat", "Shatabdi"]:
            explanations.append(f"{train_category} enjoys top operational track precedence over other passenger and freight movements.")
        else:
            explanations.append(f"{train_category} may face platform precedence halts for higher priority express services.")

        return {
            "predicted_delay_minutes": predicted_delay,
            "scheduled_arrival": scheduled_arrival,
            "predicted_arrival_time": expected_arrival,
            "delay_category": category,
            "late_probability": prob_late,
            "confidence_interval": {
                "lower": lower_bound,
                "upper": upper_bound
            },
            "model_name": self.model_name,
            "model_type": model_type,
            "model_version": model_ver,
            "explanation": explanations,
            "features_used": {
                "previous_delay": previous_station_delay,
                "distance_km": distance_km,
                "weather": weather_condition,
                "congestion": congestion_level,
                "category": train_category
            }
        }
