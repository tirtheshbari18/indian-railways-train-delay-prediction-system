import time
from collections import defaultdict
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.services.seed_data import seed_database
from backend.app.ml.model_trainer import ModelTrainingPipeline
from backend.app.models.schema import ModelRegistry, HistoricalTrainRunning

# Import API routers
from backend.app.api.auth import router as auth_router
from backend.app.api.trains import router as trains_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.routes import router as routes_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.datasets import router as datasets_router
from backend.app.api.models import router as models_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.stations_api import router as stations_router
from backend.app.api.railway_network import router as railway_network_router

# In-memory Rate Limiter
request_counts = defaultdict(list)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables and seed database
    logger.info("Initializing Railway AI database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Checking database seed records...")
        seed_database(db)
        
        # Check if model registry has models trained
        model_count = db.query(ModelRegistry).count()
        if model_count == 0:
            logger.info("No trained models found. Running initial chronological training pipeline...")
            import pandas as pd
            records = db.query(HistoricalTrainRunning).all()
            if len(records) >= 50:
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
                trainer = ModelTrainingPipeline()
                train_res = trainer.train_and_compare_all(df)
                
                # Register models
                for idx, item in enumerate(train_res["comparison"]):
                    metrics = item["metrics"]
                    is_active = (item["model_name"] == train_res["best_model_name"])
                    reg_entry = ModelRegistry(
                        model_name=item["model_name"],
                        model_type=item["model_type"],
                        model_version=item["version"],
                        artifact_path=item["artifact_path"],
                        scaler_artifact_path=item["scaler_path"],
                        mae=metrics["mae"],
                        mse=metrics["mse"],
                        rmse=metrics["rmse"],
                        r2_score=metrics["r2_score"],
                        is_active=is_active,
                        features_list=train_res["features_used"],
                        evaluation_metrics=metrics,
                        training_sample_count=item["train_rows"]
                    )
                    db.add(reg_entry)
                db.commit()
                logger.info(f"Initial model training complete. Best model: {train_res['best_model_name']}")
    except Exception as e:
        logger.error(f"Error during startup seeding/training: {e}")
    finally:
        db.close()

    yield
    logger.info("Railway AI application shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Machine Learning Platform for Indian Railways Train Delay Estimation and Punctuality Analytics",
    lifespan=lifespan
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware (Sliding Window 60s)
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    # Allow health checks without rate limiting
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    
    # Filter requests in the last 60 seconds
    timestamps = [t for t in request_counts[client_ip] if current_time - t < 60]
    if len(timestamps) >= settings.RATE_LIMIT_PER_MINUTE:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please wait a minute before making more requests."}
        )
    
    timestamps.append(current_time)
    request_counts[client_ip] = timestamps
    
    response = await call_next(request)
    return response

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(trains_router, prefix=settings.API_V1_STR)
app.include_router(predictions_router, prefix=settings.API_V1_STR)
app.include_router(routes_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(datasets_router, prefix=settings.API_V1_STR)
app.include_router(models_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(stations_router, prefix=settings.API_V1_STR)
app.include_router(railway_network_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }
