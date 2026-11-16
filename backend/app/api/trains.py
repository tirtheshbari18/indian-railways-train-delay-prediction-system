from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.database import get_db
from backend.app.models.schema import Train, TrainRoute, Station
from backend.app.schemas.pydantic_models import TrainSchema, TrainDetailSchema, StationSchema, RouteStopSchema

router = APIRouter(prefix="/trains", tags=["Trains & Stations"])

@router.get("", response_model=List[TrainSchema])
def list_trains(
    query: Optional[str] = Query(None, description="Search by train number or name"),
    category: Optional[str] = Query(None, description="Filter by train category (Rajdhani, Vande Bharat, etc.)"),
    source: Optional[str] = Query(None, description="Filter by source station code"),
    dest: Optional[str] = Query(None, description="Filter by destination station code"),
    db: Session = Depends(get_db)
):
    q = db.query(Train)
    if query:
        search_filter = or_(
            Train.train_number.ilike(f"%{query}%"),
            Train.train_name.ilike(f"%{query}%")
        )
        q = q.filter(search_filter)
    if category:
        q = q.filter(Train.train_category == category)
    if source:
        q = q.filter(Train.source_station_code == source.upper())
    if dest:
        q = q.filter(Train.dest_station_code == dest.upper())
        
    trains = q.order_by(Train.train_number).all()
    return [TrainSchema.model_validate(t) for t in trains]

@router.get("/{train_number}", response_model=TrainDetailSchema)
def get_train_details(train_number: str, db: Session = Depends(get_db)):
    train = db.query(Train).filter(Train.train_number == train_number).first()
    if not train:
        raise HTTPException(status_code=404, detail=f"Train {train_number} not found")
        
    routes = (
        db.query(TrainRoute, Station.station_name)
        .outerjoin(Station, TrainRoute.station_code == Station.station_code)
        .filter(TrainRoute.train_number == train_number)
        .order_by(TrainRoute.stop_number)
        .all()
    )
    
    stop_schemas = []
    for r, st_name in routes:
        stop_schemas.append(
            RouteStopSchema(
                station_code=r.station_code,
                station_name=st_name or r.station_code,
                stop_number=r.stop_number,
                scheduled_arrival=r.scheduled_arrival,
                scheduled_departure=r.scheduled_departure,
                halt_minutes=r.halt_minutes,
                distance_from_source_km=r.distance_from_source_km,
                day_offset=r.day_offset
            )
        )
        
    detail = TrainDetailSchema(
        train_number=train.train_number,
        train_name=train.train_name,
        train_category=train.train_category,
        source_station_code=train.source_station_code,
        dest_station_code=train.dest_station_code,
        total_distance_km=train.total_distance_km,
        runs_on_days=train.runs_on_days,
        active=train.active,
        routes=stop_schemas
    )
    return detail

@router.get("/stations/all", response_model=List[StationSchema])
def list_stations(
    search: Optional[str] = Query(None, description="Search station by name or code"),
    zone: Optional[str] = Query(None, description="Filter by railway zone"),
    db: Session = Depends(get_db)
):
    q = db.query(Station)
    if search:
        s_filter = or_(
            Station.station_code.ilike(f"%{search}%"),
            Station.station_name.ilike(f"%{search}%")
        )
        q = q.filter(s_filter)
    if zone:
        q = q.filter(Station.zone == zone.upper())
        
    stations = q.order_by(Station.station_code).all()
    return [StationSchema.model_validate(s) for s in stations]
