import os
import time
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    from sklearn.ensemble import HistGradientBoostingRegressor
    XGBOOST_AVAILABLE = False

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.ml.feature_engineering import (
    FEATURE_COLUMNS,
    extract_features_from_df,
    chronological_split
)
from backend.app.ml.evaluator import evaluate_predictions, get_feature_importances

class ModelTrainingPipeline:
    def __init__(self, artifacts_dir=None):
        self.artifacts_dir = artifacts_dir or settings.MODEL_ARTIFACTS_PATH
        os.makedirs(self.artifacts_dir, exist_ok=True)
        
    def _instantiate_model(self, model_type: str):
        if model_type == "LinearRegression":
            return LinearRegression()
        elif model_type == "RandomForest":
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "GradientBoosting":
            return GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.08,
                max_depth=5,
                random_state=42
            )
        elif model_type == "XGBoost":
            if XGBOOST_AVAILABLE:
                return xgb.XGBRegressor(
                    n_estimators=120,
                    learning_rate=0.08,
                    max_depth=6,
                    subsample=0.85,
                    colsample_bytree=0.85,
                    random_state=42,
                    n_jobs=-1
                )
            else:
                logger.info("XGBoost library not found, utilizing HistGradientBoostingRegressor fallback")
                return HistGradientBoostingRegressor(
                    max_iter=120,
                    learning_rate=0.08,
                    max_depth=6,
                    random_state=42
                )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def train_and_compare_all(
        self,
        df: pd.DataFrame,
        target_col: str = "delay_arrival_minutes",
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train all 4 candidate models using chronological train/test splitting,
        evaluate on unseen test data, and store model artifacts.
        """
        logger.info(f"Starting model training pipeline on {len(df)} historical records...")
        
        # 1. Chronological Train/Test Split
        train_df, test_df = chronological_split(df, date_col="journey_date", test_size=test_size)
        logger.info(f"Chronological split: Train records = {len(train_df)}, Test records = {len(test_df)}")
        
        # 2. Extract features
        X_train_raw = extract_features_from_df(train_df)
        y_train = train_df[target_col].fillna(0.0).values
        
        X_test_raw = extract_features_from_df(test_df)
        y_test = test_df[target_col].fillna(0.0).values
        
        # 3. Fit scaler only on training data
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_raw)
        X_test_scaled = scaler.transform(X_test_raw)
        
        # Save scaler
        scaler_filename = "standard_scaler.joblib"
        scaler_path = os.path.join(self.artifacts_dir, scaler_filename)
        joblib.dump(scaler, scaler_path)
        
        model_types = ["LinearRegression", "RandomForest", "GradientBoosting", "XGBoost"]
        comparison_results = []
        best_model_name = None
        best_mae = float("inf")
        best_model_type = None

        timestamp_str = int(time.time())

        for m_type in model_types:
            logger.info(f"Training {m_type}...")
            start_time = time.time()
            model = self._instantiate_model(m_type)
            
            # For linear models, use scaled features; for tree models, raw or scaled both work
            # For consistency, use scaled features
            model.fit(X_train_scaled, y_train)
            training_duration = time.time() - start_time
            
            # Predictions on test set
            y_pred = model.predict(X_test_scaled)
            # Clip predictions to realistic bounds (a train won't arrive 60 mins early)
            y_pred = np.clip(y_pred, -20.0, 720.0)
            
            metrics = evaluate_predictions(y_test, y_pred)
            importances = get_feature_importances(model, FEATURE_COLUMNS)
            
            model_name = f"{m_type.lower()}_v1"
            artifact_filename = f"{model_name}.joblib"
            artifact_path = os.path.join(self.artifacts_dir, artifact_filename)
            
            # Save artifact bundle: model, feature columns, scaler info, metrics
            model_bundle = {
                "model": model,
                "model_type": m_type,
                "features": FEATURE_COLUMNS,
                "metrics": metrics,
                "importances": importances,
                "train_sample_count": len(train_df),
                "test_sample_count": len(test_df),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            joblib.dump(model_bundle, artifact_path)
            
            result_item = {
                "model_name": model_name,
                "model_type": m_type,
                "version": "1.0",
                "artifact_path": artifact_path,
                "scaler_path": scaler_path,
                "metrics": metrics,
                "feature_importances": importances,
                "training_duration_seconds": round(training_duration, 2),
                "train_rows": len(train_df),
                "test_rows": len(test_df),
            }
            comparison_results.append(result_item)
            logger.info(f"{m_type} results: MAE={metrics['mae']} mins, RMSE={metrics['rmse']}, R2={metrics['r2_score']}")
            
            # Select best based on MAE (and R2)
            if metrics["mae"] < best_mae:
                best_mae = metrics["mae"]
                best_model_name = model_name
                best_model_type = m_type

        return {
            "comparison": comparison_results,
            "best_model_name": best_model_name,
            "best_model_type": best_model_type,
            "best_mae": best_mae,
            "train_sample_count": len(train_df),
            "test_sample_count": len(test_df),
            "features_used": FEATURE_COLUMNS
        }
