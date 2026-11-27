from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.database import get_db
from backend.app.models.schema import Station, StationPlatform, StationAlias
from backend.app.schemas.pydantic_models import StationDetailSchema, StationPlatformSchema

router = APIRouter(prefix="/stations", tags=["Station Master & Platforms"])

@router.get("", response_model=List[StationDetailSchema])
def list_master_stations(
    search: Optional[str] = Query(None, description="Search station by name or code"),
    zone: Optional[str] = Query(None, description="Filter by railway zone"),
    division: Optional[str] = Query(None, description="Filter by railway division"),
    limit: int = Query(200, ge=1, le=1000),
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
    if division:
        q = q.filter(Station.division == division.upper())

    stations = q.order_by(Station.station_code).limit(limit).all()

    results: List[StationDetailSchema] = []
    for s in stations:
        pfs = db.query(StationPlatform).filter(StationPlatform.station_code == s.station_code).order_by(StationPlatform.platform_number).all()
        results.append(
            StationDetailSchema(
                station_code=s.station_code,
                station_name=s.station_name,
                alternative_names=s.alternative_names or [],
                zone=s.zone,
                division=s.division,
                state=s.state,
                district=s.district,
                city=s.city,
                station_category=s.station_category,
                station_type=s.station_type,
                latitude=s.latitude,
                longitude=s.longitude,
                elevation=s.elevation,
                total_platforms=s.total_platforms,
                lines_count=s.lines_count,
                track_gauge=s.track_gauge,
                electrification_status=s.electrification_status,
                platforms=[StationPlatformSchema.model_validate(p) for p in pfs]
            )
        )
    return results

@router.get("/{station_code}", response_model=StationDetailSchema)
def get_station_detail(station_code: str, db: Session = Depends(get_db)):
    code = station_code.strip().upper()
    s = db.query(Station).filter(Station.station_code == code).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"Station {code} not found")

    pfs = db.query(StationPlatform).filter(StationPlatform.station_code == code).order_by(StationPlatform.platform_number).all()
    return StationDetailSchema(
        station_code=s.station_code,
        station_name=s.station_name,
        alternative_names=s.alternative_names or [],
        zone=s.zone,
        division=s.division,
        state=s.state,
        district=s.district,
        city=s.city,
        station_category=s.station_category,
        station_type=s.station_type,
        latitude=s.latitude,
        longitude=s.longitude,
        elevation=s.elevation,
        total_platforms=s.total_platforms,
        lines_count=s.lines_count,
        track_gauge=s.track_gauge,
        electrification_status=s.electrification_status,
        platforms=[StationPlatformSchema.model_validate(p) for p in pfs]
    )

@router.get("/{station_code}/platforms", response_model=List[StationPlatformSchema])
def get_station_platforms(station_code: str, db: Session = Depends(get_db)):
    code = station_code.strip().upper()
    pfs = db.query(StationPlatform).filter(StationPlatform.station_code == code).order_by(StationPlatform.platform_number).all()
    return [StationPlatformSchema.model_validate(p) for p in pfs]
