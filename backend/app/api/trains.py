from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.database import get_db
from backend.app.models.schema import Train, TrainRoute, Station, TrainCategory, PlatformAssignment
from backend.app.schemas.pydantic_models import (
    TrainSchema, TrainDetailSchema, StationSchema, RouteStopSchema,
    TrainBetweenStationsResult, LiveTrainRunningResponse, LiveRunningStop
)

router = APIRouter(prefix="/trains", tags=["Trains & Stations"])

@router.get("", response_model=List[TrainSchema])
def list_trains(
    query: Optional[str] = Query(None, description="Search by train number or name"),
    category: Optional[str] = Query(None, description="Filter by train category (Rajdhani, Vande Bharat, etc.)"),
    source: Optional[str] = Query(None, description="Filter by source station code"),
    dest: Optional[str] = Query(None, description="Filter by destination station code"),
    limit: int = Query(100, ge=1, le=500),
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
        
    trains = q.order_by(Train.train_number).limit(limit).all()
    return [TrainSchema.model_validate(t) for t in trains]

@router.get("/categories")
def list_train_categories(db: Session = Depends(get_db)):
    cats = db.query(TrainCategory).all()
    if cats:
        return [{"code": c.category_code, "name": c.category_name, "priority": c.priority_level} for c in cats]
    # Default fallback
    return [
        {"code": "SF", "name": "Superfast Express", "priority": 3},
        {"code": "EXP", "name": "Express", "priority": 4},
        {"code": "VB", "name": "Vande Bharat", "priority": 1},
        {"code": "RAJ", "name": "Rajdhani", "priority": 1},
        {"code": "SHT", "name": "Shatabdi", "priority": 2},
        {"code": "MEMU", "name": "Mainline Electric Multiple Unit", "priority": 6},
        {"code": "EMU", "name": "Suburban Local (AC/Regular)", "priority": 5},
    ]

@router.get("/between-stations", response_model=List[TrainBetweenStationsResult])
def get_trains_between_stations(
    source: str = Query(..., description="Originating/boarding station code (e.g. BOR)"),
    destination: str = Query(..., description="Destination station code (e.g. DRD)"),
    day: Optional[str] = Query(None, description="Day of week (Mon, Tue, etc.)"),
    category: Optional[str] = Query(None, description="Train category filter"),
    bidirectional: bool = Query(False, description="Include both directions on this corridor"),
    db: Session = Depends(get_db)
):
    src_code = source.strip().upper()
    dst_code = destination.strip().upper()

    stations_map = {
        s.station_code: s.station_name
        for s in db.query(Station).filter(Station.station_code.in_([src_code, dst_code])).all()
    }

    def fetch_direction(from_code: str, to_code: str):
        from_name = stations_map.get(from_code, from_code)
        to_name = stations_map.get(to_code, to_code)
        r_from = db.query(TrainRoute).filter(TrainRoute.station_code == from_code).subquery()
        r_to = db.query(TrainRoute).filter(TrainRoute.station_code == to_code).subquery()

        query_res = (
            db.query(
                Train,
                r_from.c.stop_number.label("src_stop_no"),
                r_from.c.scheduled_departure.label("src_dep"),
                r_from.c.distance_from_source_km.label("src_dist"),
                r_from.c.verified_platform.label("src_pf"),
                r_to.c.stop_number.label("dst_stop_no"),
                r_to.c.scheduled_arrival.label("dst_arr"),
                r_to.c.distance_from_source_km.label("dst_dist"),
                r_to.c.verified_platform.label("dst_pf"),
            )
            .join(r_from, Train.train_number == r_from.c.train_number)
            .join(r_to, Train.train_number == r_to.c.train_number)
            .filter(r_from.c.stop_number < r_to.c.stop_number)
        )
        if category:
            query_res = query_res.filter(Train.train_category == category)
        return query_res.all(), from_name, to_name

    matched_rows, src_name, dst_name = fetch_direction(src_code, dst_code)
    all_matched = [(row, src_code, dst_code, src_name, dst_name) for row in matched_rows]

    if bidirectional:
        rev_rows, r_src_name, r_dst_name = fetch_direction(dst_code, src_code)
        all_matched.extend([(row, dst_code, src_code, r_src_name, r_dst_name) for row in rev_rows])

    output: List[TrainBetweenStationsResult] = []

    def parse_time_mins(t_str: Optional[str]) -> int:
        if not t_str or ":" not in t_str:
            return 0
        try:
            h, m = map(int, t_str.split(":"))
            return h * 60 + m
        except Exception:
            return 0

    for (tr, s_no, s_dep, s_dist, s_pf, d_no, d_arr, d_dist, d_pf), f_code, t_code, f_name, t_name in all_matched:
        if day and tr.runs_on_days != "Daily":
            if day[:3] not in tr.runs_on_days:
                continue

        dist_diff = round(max(0.0, float(d_dist) - float(s_dist)), 1)
        t_src_mins = parse_time_mins(s_dep)
        t_dst_mins = parse_time_mins(d_arr)
        dur_mins = (t_dst_mins - t_src_mins) if t_dst_mins >= t_src_mins else (1440 - t_src_mins + t_dst_mins)
        dur_hours = dur_mins // 60
        dur_rem = dur_mins % 60
        dur_str = f"{dur_hours}h {dur_rem}m" if dur_hours > 0 else f"{dur_rem}m"

        intermediate_stops = max(0, int(d_no) - int(s_no) - 1)

        output.append(
            TrainBetweenStationsResult(
                train_number=tr.train_number,
                train_name=tr.train_name,
                train_category=tr.train_category,
                train_type=getattr(tr, "train_type", "Express") or "Express",
                runs_on_days=tr.runs_on_days,
                source_code=f_code,
                source_name=f_name,
                source_departure=s_dep or "Source",
                source_platform=s_pf if s_pf and s_pf != "Not Available" else "1",
                dest_code=t_code,
                dest_name=t_name,
                dest_arrival=d_arr or "Destination",
                dest_platform=d_pf if d_pf and d_pf != "Not Available" else "2",
                travel_distance_km=dist_diff,
                travel_duration_minutes=dur_mins,
                travel_duration_str=dur_str,
                intermediate_stops_count=intermediate_stops,
                is_commercial_stop=True
            )
        )

    output.sort(key=lambda x: parse_time_mins(x.source_departure))
    return output

@router.get("/{train_number}/live", response_model=LiveTrainRunningResponse)
def get_live_train_status(train_number: str, db: Session = Depends(get_db)):
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

    if not routes:
        raise HTTPException(status_code=404, detail="Route not found for train")

    # Stations dictionary
    st_dict = {
        s.station_code: s.station_name
        for s in db.query(Station).filter(Station.station_code.in_([r.station_code for r, _ in routes])).all()
    }

    # Simulate realistic live state based on time of day
    now = datetime.now()
    now_mins = now.hour * 60 + now.minute

    stops_timeline: List[LiveRunningStop] = []
    current_idx = 0
    active_delay = 6.0 if "Rajdhani" in train.train_category or "Vande" in train.train_category else 14.0

    def parse_t(t_s: Optional[str]) -> int:
        if not t_s or ":" not in t_s:
            return 0
        try:
            h, m = map(int, t_s.split(":"))
            return h * 60 + m
        except Exception:
            return 0

    def add_mins(t_s: Optional[str], mins: float) -> str:
        if not t_s or ":" not in t_s:
            return "--:--"
        try:
            h, m = map(int, t_s.split(":"))
            total = (h * 60 + m + int(round(mins))) % 1440
            return f"{total // 60:02d}:{total % 60:02d}"
        except Exception:
            return t_s

    total_stops = len(routes)
    # Determine which stop the train is currently near
    for idx, (r, st_name) in enumerate(routes):
        dep_m = parse_t(r.scheduled_departure or r.scheduled_arrival)
        if dep_m <= now_mins or idx == 0:
            current_idx = idx

    current_idx = min(current_idx, max(0, total_stops - 1))

    for idx, (r, st_name) in enumerate(routes):
        station_title = st_name or st_dict.get(r.station_code, r.station_code)
        sched_arr = r.scheduled_arrival
        sched_dep = r.scheduled_departure

        if idx < current_idx:
            status = "Departed"
            arr_delay = active_delay * (idx / max(1, current_idx))
            dep_delay = arr_delay + 1.0
        elif idx == current_idx:
            status = "Current"
            arr_delay = active_delay
            dep_delay = active_delay
        elif idx == current_idx + 1:
            status = "Next"
            arr_delay = active_delay + 2.0
            dep_delay = arr_delay
        else:
            status = "Upcoming"
            arr_delay = active_delay + 4.0
            dep_delay = arr_delay

        act_arr = add_mins(sched_arr, arr_delay) if sched_arr else None
        act_dep = add_mins(sched_dep, dep_delay) if sched_dep else None

        pf_val = r.verified_platform if r.verified_platform and r.verified_platform != "Not Available" else "1"

        stops_timeline.append(
            LiveRunningStop(
                stop_number=r.stop_number,
                station_code=r.station_code,
                station_name=station_title,
                scheduled_arrival=sched_arr,
                scheduled_departure=sched_dep,
                actual_arrival=act_arr,
                actual_departure=act_dep,
                delay_arrival_minutes=round(arr_delay, 1),
                delay_departure_minutes=round(dep_delay, 1),
                platform=pf_val,
                distance_km=r.distance_from_source_km,
                status=status
            )
        )

    current_stop_data = stops_timeline[current_idx]
    delay_category = "On-Time (0-15m)"
    if active_delay > 120:
        delay_category = "Severe Delay (>120m)"
    elif active_delay > 45:
        delay_category = "Moderate Delay (45-120m)"
    elif active_delay > 15:
        delay_category = "Slight Delay (15-45m)"

    return LiveTrainRunningResponse(
        train_number=train.train_number,
        train_name=train.train_name,
        train_category=train.train_category,
        source_station_code=train.source_station_code,
        source_station_name=st_dict.get(train.source_station_code, train.source_station_code),
        dest_station_code=train.dest_station_code,
        dest_station_name=st_dict.get(train.dest_station_code, train.dest_station_code),
        current_status=f"Departed {current_stop_data.station_name}" if current_idx > 0 else f"Stationed at {current_stop_data.station_name}",
        current_station_code=current_stop_data.station_code,
        current_station_name=current_stop_data.station_name,
        delay_minutes=round(active_delay, 1),
        delay_category=delay_category,
        last_reported_time=datetime.now().strftime("%H:%M:%S"),
        timeline=stops_timeline
    )

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
        
    stations = q.order_by(Station.station_code).limit(limit).all()
    return [StationSchema.model_validate(s) for s in stations]
