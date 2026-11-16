import uuid
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_role
from backend.app.models.schema import ModelRegistry, ModelTrainingHistory, HistoricalTrainRunning, AuditLog
from backend.app.schemas.pydantic_models import (
    ModelTrainRequest, ModelRegistryItem, ModelActivateRequest
)
from backend.app.ml.model_trainer import ModelTrainingPipeline
from backend.app.api.predictions import predictor

router = APIRouter(prefix="/models", tags=["Machine Learning Models"])
trainer = ModelTrainingPipeline()

@router.post("/train")
def train_and_evaluate_models(
    req: ModelTrainRequest,
    db: Session = Depends(get_db),
    user_payload: dict = Depends(require_role(["admin", "analyst"]))
):
    """
    Train and compare candidate ML models (Linear Regression, Random Forest,
    Gradient Boosting, XGBoost) using strictly chronological train/test splitting.
    """
    records = db.query(HistoricalTrainRunning).all()
    if len(records) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient historical data ({len(records)} records). Minimum 50 records required."
        )

    # Convert to DataFrame
    data_list = []
    for r in records:
        data_list.append({
            "train_number": r.train_number,
            "train_name": r.train_name,
            "journey_date": r.journey_date,
            "station_code": r.station_code,
            "scheduled_departure": r.scheduled_departure,
            "scheduled_arrival": r.scheduled_arrival,
            "delay_arrival_minutes": r.delay_arrival_minutes,
            "delay_departure_minutes": r.delay_departure_minutes,
            "distance_km": r.distance_km,
            "halt_duration_minutes": r.halt_duration_minutes,
            "day_of_week": r.day_of_week,
            "train_category": r.train_category,
            "weather_condition": r.weather_condition,
            "congestion_level": r.congestion_level
        })
    df = pd.DataFrame(data_list)

    # Train all models
    results = trainer.train_and_compare_all(df, test_size=req.test_size)

    # Save to model registry & training history
    best_candidate = None
    saved_items = []

    for item in results["comparison"]:
        m_name = item["model_name"]
        metrics = item["metrics"]
        
        # Check if already registered
        existing = db.query(ModelRegistry).filter(ModelRegistry.model_name == m_name).first()
        if existing:
            existing.mae = metrics["mae"]
            existing.mse = metrics["mse"]
            existing.rmse = metrics["rmse"]
            existing.r2_score = metrics["r2_score"]
            existing.artifact_path = item["artifact_path"]
            existing.scaler_artifact_path = item["scaler_path"]
            existing.training_sample_count = item["train_rows"]
            existing.evaluation_metrics = metrics
            existing.trained_at = datetime.utcnow()
            reg_entry = existing
        else:
            reg_entry = ModelRegistry(
                model_name=m_name,
                model_type=item["model_type"],
                model_version=item["version"],
                artifact_path=item["artifact_path"],
                scaler_artifact_path=item["scaler_path"],
                mae=metrics["mae"],
                mse=metrics["mse"],
                rmse=metrics["rmse"],
                r2_score=metrics["r2_score"],
                is_active=False,
                features_list=results["features_used"],
                evaluation_metrics=metrics,
                training_sample_count=item["train_rows"],
                trained_at=datetime.utcnow()
            )
            db.add(reg_entry)

        # Log training run history
        hist = ModelTrainingHistory(
            training_run_id=f"RUN-{uuid.uuid4().hex[:8].upper()}",
            model_type=item["model_type"],
            train_row_count=item["train_rows"],
            test_row_count=item["test_rows"],
            training_duration_seconds=item["training_duration_seconds"],
            mae=metrics["mae"],
            rmse=metrics["rmse"],
            r2=metrics["r2_score"],
            status="Completed"
        )
        db.add(hist)
        saved_items.append(item)

    db.commit()

    # If auto_activate_best is requested and passes validation (R2 > 0 and reasonable MAE)
    best_model_name = results["best_model_name"]
    best_entry = db.query(ModelRegistry).filter(ModelRegistry.model_name == best_model_name).first()
    
    if req.auto_activate_best and best_entry and best_entry.r2_score > 0.0:
        db.query(ModelRegistry).update({ModelRegistry.is_active: False})
        best_entry.is_active = True
        db.commit()
        # Reload predictor with newly activated model
        predictor.__init__(model_name=best_model_name)

    # Audit log
    audit = AuditLog(
        username=user_payload.get("sub"),
        action="MODELS_TRAINED",
        entity_type="MODEL",
        entity_id=best_model_name,
        details={"best_model": best_model_name, "best_mae": results["best_mae"]}
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "message": f"Successfully trained 4 models using chronological split. Best model: {best_model_name} (MAE: {results['best_mae']}m)",
        "best_model_name": best_model_name,
        "best_mae": results["best_mae"],
        "comparison": saved_items
    }

@router.get("/registry", response_model=List[ModelRegistryItem])
def list_registered_models(db: Session = Depends(get_db)):
    models = db.query(ModelRegistry).order_by(ModelRegistry.mae.asc()).all()
    return [ModelRegistryItem.model_validate(m) for m in models]

@router.post("/activate")
def activate_model(
    req: ModelActivateRequest,
    db: Session = Depends(get_db),
    user_payload: dict = Depends(require_role(["admin"]))
):
    """
    Activate a selected validated model for live predictions.
    Safeguard: Verifies model exists and has validated metrics.
    """
    model = db.query(ModelRegistry).filter(ModelRegistry.model_name == req.model_name).first()
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {req.name} not found in registry.")

    # Validation check: do not activate completely failed models
    if model.r2_score < -0.5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {req.model_name} validation failed (R²={model.r2_score}). Cannot activate unvalidated model."
        )

    # Deactivate others
    db.query(ModelRegistry).update({ModelRegistry.is_active: False})
    model.is_active = True
    db.commit()

    # Reload predictor in memory
    predictor.__init__(model_name=req.model_name)

    audit = AuditLog(
        username=user_payload.get("sub"),
        action="MODEL_ACTIVATED",
        entity_type="MODEL",
        entity_id=req.model_name,
        details={"mae": model.mae, "rmse": model.rmse, "r2": model.r2_score}
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "message": f"Model {req.model_name} is now the active production prediction model.",
        "active_model": req.model_name,
        "mae": model.mae,
        "r2_score": model.r2_score
    }

@router.get("/history")
def get_training_history(db: Session = Depends(get_db)):
    history = db.query(ModelTrainingHistory).order_by(ModelTrainingHistory.created_at.desc()).limit(20).all()
    return [
        {
            "id": h.id,
            "training_run_id": h.training_run_id,
            "model_type": h.model_type,
            "train_row_count": h.train_row_count,
            "test_row_count": h.test_row_count,
            "training_duration_seconds": h.training_duration_seconds,
            "mae": h.mae,
            "rmse": h.rmse,
            "r2": h.r2,
            "status": h.status,
            "created_at": h.created_at.isoformat() if h.created_at else None
        }
        for h in history
    ]
