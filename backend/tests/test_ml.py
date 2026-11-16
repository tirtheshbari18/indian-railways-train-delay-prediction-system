import pytest
import numpy as np
import pandas as pd
import datetime
from backend.app.ml.feature_engineering import extract_features_from_df, chronological_split, FEATURE_COLUMNS
from backend.app.ml.evaluator import evaluate_predictions, get_feature_importances
from backend.app.ml.model_trainer import ModelTrainingPipeline
from backend.app.ml.predictor import TrainDelayPredictor

def create_mock_historical_data():
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(60)]
    records = []
    for i, d in enumerate(dates):
        records.append({
            "train_number": "12951" if i % 2 == 0 else "22436",
            "train_name": "Test Express",
            "journey_date": d,
            "station_code": "NDLS" if i % 3 == 0 else "CNB",
            "scheduled_departure": "08:00",
            "scheduled_arrival": "14:00",
            "delay_arrival_minutes": float((i % 7) * 5.0 + 2.0),
            "delay_departure_minutes": float((i % 7) * 5.0 + 3.0),
            "distance_km": float(100 + i * 5),
            "halt_duration_minutes": 5.0,
            "day_of_week": d.strftime("%A"),
            "train_category": "Rajdhani" if i % 2 == 0 else "Vande Bharat",
            "weather_condition": "Fog" if i % 5 == 0 else "Clear",
            "congestion_level": "High" if i % 4 == 0 else "Normal"
        })
    return pd.DataFrame(records)

def test_chronological_split():
    df = create_mock_historical_data()
    train_df, test_df = chronological_split(df, date_col="journey_date", test_size=0.2)
    
    assert len(train_df) + len(test_df) == len(df)
    # Ensure strict temporal ordering: max train date <= min test date
    max_train_date = train_df["journey_date"].max()
    min_test_date = test_df["journey_date"].min()
    assert max_train_date <= min_test_date, "Temporal leakage detected! Train dates must precede test dates."

def test_feature_extraction():
    df = create_mock_historical_data()
    features = extract_features_from_df(df)
    assert list(features.columns) == FEATURE_COLUMNS
    assert len(features) == len(df)
    # Check for NaN values
    assert features.isna().sum().sum() == 0, "Feature set contains unexpected NaN values."

def test_evaluation_metrics():
    y_true = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    y_pred = np.array([12.0, 18.0, 33.0, 39.0, 48.0])
    metrics = evaluate_predictions(y_true, y_pred)
    
    assert "mae" in metrics
    assert "rmse" in metrics
    assert "r2_score" in metrics
    assert metrics["mae"] > 0
    assert metrics["r2_score"] > 0.9

def test_model_training_pipeline(tmp_path):
    df = create_mock_historical_data()
    pipeline = ModelTrainingPipeline(artifacts_dir=str(tmp_path))
    result = pipeline.train_and_compare_all(df, test_size=0.25)
    
    assert "comparison" in result
    assert len(result["comparison"]) == 4 # Linear, RF, GBR, XGBoost
    assert result["best_model_name"] is not None
    assert result["best_mae"] >= 0.0

def test_predictor_inference():
    predictor = TrainDelayPredictor()
    pred = predictor.predict_delay(
        train_number="12951",
        train_category="Rajdhani",
        distance_km=450.0,
        scheduled_departure="16:55",
        scheduled_arrival="22:30",
        journey_date="2026-11-20",
        previous_station_delay=10.0,
        weather_condition="Clear",
        congestion_level="Normal"
    )
    
    assert "predicted_delay_minutes" in pred
    assert "predicted_arrival_time" in pred
    assert "delay_category" in pred
    assert "confidence_interval" in pred
    assert "late_probability" in pred
    assert 0.0 <= pred["late_probability"] <= 1.0
    assert pred["confidence_interval"]["lower"] <= pred["confidence_interval"]["upper"]
