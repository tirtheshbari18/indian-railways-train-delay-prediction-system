import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import require_role
from backend.app.models.schema import ImportedDataset, HistoricalTrainRunning, AuditLog
from backend.app.schemas.pydantic_models import DatasetSummary, HistoricalRunningRecord
from backend.app.services.data_processor import RailwayDataProcessor

router = APIRouter(prefix="/datasets", tags=["Dataset Management"])
processor = RailwayDataProcessor()

@router.post("/upload", response_model=DatasetSummary)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_payload: dict = Depends(require_role(["admin", "analyst"]))
):
    """
    Upload and process railway operational datasets in CSV, Excel or JSON formats.
    Performs data cleaning, validation, deduplication and feature engineering.
    """
    filename = file.filename or "unknown_dataset.csv"
    ext = filename.split(".")[-1].lower()
    if ext not in ["csv", "xlsx", "xls", "json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '.{ext}'. Supported formats: CSV, Excel (.xlsx, .xls), JSON"
        )

    content = await file.read()
    
    # Save original file to data directory
    dest_path = settings.DATA_PATH / f"imported_{int(os.times().system)}_{filename}"
    with open(dest_path, "wb") as f:
        f.write(content)

    try:
        raw_df = processor.load_file_to_df(content, filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse file: {str(e)}"
        )

    try:
        clean_df, report = processor.validate_and_clean_data(raw_df)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Data validation failed: {str(e)}"
        )

    # Insert cleaned records into database
    records_to_insert = []
    for _, row in clean_df.iterrows():
        rec = HistoricalTrainRunning(
            train_number=str(row["train_number"]),
            train_name=str(row.get("train_name", f"Train {row['train_number']}")),
            journey_date=row["journey_date"],
            station_code=str(row["station_code"]),
            scheduled_arrival=str(row.get("scheduled_arrival", "12:00")),
            actual_arrival=str(row.get("actual_arrival", "12:00")),
            scheduled_departure=str(row.get("scheduled_departure", "12:05")),
            actual_departure=str(row.get("actual_departure", "12:05")),
            delay_arrival_minutes=float(row.get("delay_arrival_minutes", 0.0)),
            delay_departure_minutes=float(row.get("delay_departure_minutes", 0.0)),
            distance_km=float(row.get("distance_km", 50.0)),
            halt_duration_minutes=float(row.get("halt_duration_minutes", 2.0)),
            day_of_week=str(row.get("day_of_week", "")),
            train_category=str(row.get("train_category", "Express")),
            weather_condition=str(row.get("weather_condition", "Clear")),
            congestion_level=str(row.get("congestion_level", "Normal"))
        )
        records_to_insert.append(rec)

    db.bulk_save_objects(records_to_insert)

    # Record in imported_datasets
    dataset_rec = ImportedDataset(
        dataset_name=filename,
        file_type=ext,
        file_path=str(dest_path),
        total_records=report["initial_rows"],
        valid_records=report["final_clean_rows"],
        invalid_records=report["invalid_rows_dropped"],
        cleaning_summary=report,
        status="Ready",
        notes=f"Uploaded and processed by {user_payload.get('sub', 'system')}."
    )
    db.add(dataset_rec)
    db.commit()
    db.refresh(dataset_rec)

    # Audit log
    audit = AuditLog(
        username=user_payload.get("sub"),
        action="DATASET_UPLOADED",
        entity_type="DATASET",
        entity_id=str(dataset_rec.id),
        details={"filename": filename, "records": len(clean_df)}
    )
    db.add(audit)
    db.commit()

    return DatasetSummary.model_validate(dataset_rec)

@router.get("", response_model=List[DatasetSummary])
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(ImportedDataset).order_by(ImportedDataset.upload_timestamp.desc()).all()
    return [DatasetSummary.model_validate(d) for d in datasets]

@router.get("/{dataset_id}", response_model=DatasetSummary)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    ds = db.query(ImportedDataset).filter(ImportedDataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DatasetSummary.model_validate(ds)

@router.get("/{dataset_id}/records", response_model=List[HistoricalRunningRecord])
def preview_dataset_records(
    dataset_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    records = db.query(HistoricalTrainRunning).order_by(HistoricalTrainRunning.id.desc()).limit(limit).all()
    return [HistoricalRunningRecord.model_validate(r) for r in records]
