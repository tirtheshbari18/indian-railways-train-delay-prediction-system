from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.pydantic_models import RouteDelayPredictionRequest, RouteDelayPredictionResponse
from backend.app.services.route_engine import RouteDelayPredictionEngine
from backend.app.api.predictions import predictor

router = APIRouter(prefix="/routes", tags=["Route Delay Engine"])

route_engine = RouteDelayPredictionEngine(predictor)

@router.post("/predict-intermediate-delays", response_model=RouteDelayPredictionResponse)
def predict_intermediate_delays(
    req: RouteDelayPredictionRequest,
    db: Session = Depends(get_db)
):
    try:
        result = route_engine.predict_route_delays(
            db=db,
            train_number=req.train_number,
            journey_date=req.journey_date,
            initial_delay_minutes=req.initial_delay_minutes or 0.0,
            weather_condition=req.weather_condition or "Clear"
        )
        return RouteDelayPredictionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate route predictions: {e}")
