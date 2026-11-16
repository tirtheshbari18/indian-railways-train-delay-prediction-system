import uuid
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_payload
from backend.app.models.schema import Train, TrainRoute, Station, PredictionResult, PredictionFeature, AuditLog
from backend.app.schemas.pydantic_models import TrainDelayPredictionRequest, TrainDelayPredictionResponse
from backend.app.ml.predictor import TrainDelayPredictor

router = APIRouter(prefix="/predictions", tags=["Predictions"])

# Singleton predictor instance
predictor = TrainDelayPredictor()

@router.post("/predict-delay", response_model=TrainDelayPredictionResponse)
def predict_train_delay(
    req: TrainDelayPredictionRequest,
    db: Session = Depends(get_db),
    user_payload: dict = Depends(get_current_user_payload)
):
    train = db.query(Train).filter(Train.train_number == req.train_number).first()
    train_name = req.train_name or (train.train_name if train else f"Train {req.train_number}")
    category = req.train_category or (train.train_category if train else "Express")
    
    target_station = req.target_station or req.destination_station
    
    # Calculate distance to target station if routes are available
    distance_km = 350.0
    halt_duration = 2.0
    scheduled_arr = req.scheduled_arrival or "14:00"
    scheduled_dep = req.scheduled_departure or "08:00"

    if train:
        target_route = (
            db.query(TrainRoute)
            .filter(TrainRoute.train_number == req.train_number, TrainRoute.station_code == target_station.upper())
            .first()
        )
        if target_route:
            distance_km = float(target_route.distance_from_source_km or 350.0)
            halt_duration = float(target_route.halt_minutes or 2.0)
            if target_route.scheduled_arrival:
                scheduled_arr = target_route.scheduled_arrival
            if target_route.scheduled_departure and not req.scheduled_departure:
                scheduled_dep = target_route.scheduled_departure
        else:
            distance_km = float(train.total_distance_km or 500.0)

    # Perform ML Inference
    result = predictor.predict_delay(
        train_number=req.train_number,
        train_category=category,
        distance_km=distance_km,
        scheduled_departure=scheduled_dep,
        scheduled_arrival=scheduled_arr,
        journey_date=str(req.journey_date),
        previous_station_delay=float(req.previous_station_delay or 0.0),
        halt_duration_minutes=halt_duration,
        weather_condition=req.weather_condition or "Clear",
        congestion_level=req.congestion_level or "Normal"
    )

    pred_id = f"PRED-{uuid.uuid4().hex[:10].upper()}"

    # Save to database
    db_pred = PredictionResult(
        prediction_id=pred_id,
        train_number=req.train_number,
        train_name=train_name,
        source_station=req.source_station.upper(),
        dest_station=req.destination_station.upper(),
        target_station=target_station.upper(),
        journey_date=req.journey_date,
        scheduled_arrival=scheduled_arr,
        predicted_arrival_time=result["predicted_arrival_time"],
        predicted_delay_minutes=result["predicted_delay_minutes"],
        confidence_interval_lower=result["confidence_interval"]["lower"],
        confidence_interval_upper=result["confidence_interval"]["upper"],
        late_probability=result["late_probability"],
        delay_category=result["delay_category"],
        model_name=result["model_name"],
        model_version=result["model_version"],
    )
    db.add(db_pred)
    db.flush()

    db_feat = PredictionFeature(
        prediction_id=pred_id,
        feature_payload=result["features_used"]
    )
    db.add(db_feat)
    
    # Audit log
    audit = AuditLog(
        username=user_payload.get("sub", "guest"),
        action="PREDICTION_GENERATED",
        entity_type="PREDICTION",
        entity_id=pred_id,
        details={
            "train_number": req.train_number,
            "predicted_delay": result["predicted_delay_minutes"],
            "category": result["delay_category"]
        }
    )
    db.add(audit)
    db.commit()

    return TrainDelayPredictionResponse(
        prediction_id=pred_id,
        train_number=req.train_number,
        train_name=train_name,
        source_station=req.source_station.upper(),
        destination_station=req.destination_station.upper(),
        target_station=target_station.upper(),
        journey_date=req.journey_date,
        scheduled_arrival=scheduled_arr,
        predicted_arrival_time=result["predicted_arrival_time"],
        predicted_delay_minutes=result["predicted_delay_minutes"],
        confidence_interval=result["confidence_interval"],
        late_probability=result["late_probability"],
        delay_category=result["delay_category"],
        model_name=result["model_name"],
        model_version=result["model_version"],
        explanation=result["explanation"],
        disclaimer="AI Machine Learning prediction based on historical operational patterns. Not real-time GPS tracking."
    )

@router.get("/history")
def get_prediction_history(
    train_number: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    q = db.query(PredictionResult)
    if train_number:
        q = q.filter(PredictionResult.train_number == train_number)
    results = q.order_by(PredictionResult.created_at.desc()).limit(limit).all()
    
    return [
        {
            "prediction_id": r.prediction_id,
            "train_number": r.train_number,
            "train_name": r.train_name,
            "source_station": r.source_station,
            "dest_station": r.dest_station,
            "target_station": r.target_station,
            "journey_date": r.journey_date.isoformat(),
            "scheduled_arrival": r.scheduled_arrival,
            "predicted_arrival_time": r.predicted_arrival_time,
            "predicted_delay_minutes": r.predicted_delay_minutes,
            "confidence_interval": {
                "lower": r.confidence_interval_lower,
                "upper": r.confidence_interval_upper
            },
            "late_probability": r.late_probability,
            "delay_category": r.delay_category,
            "model_name": r.model_name,
            "actual_delay_minutes": r.actual_delay_minutes,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in results
    ]
