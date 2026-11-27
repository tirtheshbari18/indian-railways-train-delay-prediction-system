from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.schema import (
    RailwayZone, RailwayDivision, RailwayDistance, RailwayOperationalEvent, Station
)
from backend.app.schemas.pydantic_models import (
    RailwayZoneSchema, RailwayDivisionSchema, RailwayDistanceSchema, OperationalEventSchema
)

router = APIRouter(prefix="/railway", tags=["Railway Network Architecture & Operations"])

@router.get("/zones", response_model=List[RailwayZoneSchema])
def get_railway_zones(db: Session = Depends(get_db)):
    zones = db.query(RailwayZone).order_by(RailwayZone.zone_code).all()
    results: List[RailwayZoneSchema] = []
    for z in zones:
        divs = db.query(RailwayDivision).filter(RailwayDivision.zone_code == z.zone_code).all()
        results.append(
            RailwayZoneSchema(
                zone_code=z.zone_code,
                zone_name=z.zone_name,
                headquarters=z.headquarters,
                founded_year=getattr(z, "established_year", None),
                total_route_km=z.total_route_km,
                divisions=[
                    RailwayDivisionSchema(
                        division_code=d.division_code,
                        division_name=d.division_name,
                        headquarters=d.headquarters,
                        route_km=getattr(d, "route_km", None) or 0.0
                    )
                    for d in divs
                ]
            )
        )
    return results

@router.get("/distances", response_model=List[RailwayDistanceSchema])
def get_railway_distances(
    from_code: Optional[str] = Query(None),
    to_code: Optional[str] = Query(None),
    consecutive_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    q = db.query(RailwayDistance)
    if from_code:
        q = q.filter(RailwayDistance.from_station_code == from_code.upper())
    if to_code:
        q = q.filter(RailwayDistance.to_station_code == to_code.upper())
    if consecutive_only:
        q = q.filter(RailwayDistance.is_consecutive == True)

    distances = q.order_by(RailwayDistance.from_station_code, RailwayDistance.distance_km).all()
    return [RailwayDistanceSchema.model_validate(d) for d in distances]

@router.get("/operational-events", response_model=List[OperationalEventSchema])
def get_operational_events(
    station: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(RailwayOperationalEvent)
    if station:
        q = q.filter(RailwayOperationalEvent.station_code == station.upper())
    if event_type:
        q = q.filter(RailwayOperationalEvent.event_type.ilike(f"%{event_type}%"))

    events = q.all()
    st_dict = {
        s.station_code: s.station_name
        for s in db.query(Station).all()
    }

    results: List[OperationalEventSchema] = []
    for ev in events:
        results.append(
            OperationalEventSchema(
                id=ev.id,
                station_code=ev.station_code,
                station_name=st_dict.get(ev.station_code, ev.station_code),
                first_train_number=ev.first_train_number,
                first_train_name=ev.first_train_name,
                second_train_number=ev.second_train_number,
                second_train_name=ev.second_train_name,
                event_type=ev.event_type,
                scheduled_time=ev.scheduled_time,
                track_line=ev.track_line,
                verification_status=ev.verification_status,
                description=f"{ev.first_train_name} ({ev.first_train_number}) and {ev.second_train_name} ({ev.second_train_number}) scheduled {ev.event_type} at {ev.station_code} at {ev.scheduled_time}."
            )
        )
    return results

@router.get("/map-network")
def get_railway_map_network(db: Session = Depends(get_db)):
    """Provides station coordinates, connectivity edges, and zone bounding boxes for Leaflet."""
    stations = db.query(Station).filter(Station.latitude.isnot(None), Station.longitude.isnot(None)).all()
    distances = db.query(RailwayDistance).filter(RailwayDistance.is_consecutive == True).all()

    st_nodes = [
        {
            "code": s.station_code,
            "name": s.station_name,
            "lat": s.latitude,
            "lng": s.longitude,
            "zone": s.zone,
            "division": s.division,
            "platforms": s.total_platforms,
            "category": s.station_category,
            "type": s.station_type
        }
        for s in stations
    ]

    edges = []
    st_lookup = {s.station_code: (s.latitude, s.longitude) for s in stations}
    for d in distances:
        if d.from_station_code in st_lookup and d.to_station_code in st_lookup:
            from_coords = st_lookup[d.from_station_code]
            to_coords = st_lookup[d.to_station_code]
            edges.append({
                "from_code": d.from_station_code,
                "to_code": d.to_station_code,
                "distance_km": d.distance_km,
                "section": d.section_name,
                "coordinates": [from_coords, to_coords]
            })

    return {
        "nodes": st_nodes,
        "edges": edges,
        "total_stations": len(st_nodes),
        "total_tracks": len(edges)
    }
