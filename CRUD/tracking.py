from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models, schemas

def create_tracking(db: Session, tracking: schemas.TrackingCreate):
    db_tracking = models.Tracking(**tracking.dict())
    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)
    return db_tracking

def get_tracking(db: Session, tracking_id: int):
    tracking = db.query(models.Tracking).filter(models.Tracking.id == tracking_id).first()
    if tracking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking not found")
    return tracking

def get_trackings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tracking).offset(skip).limit(limit).all()

def update_tracking(db: Session, tracking_id: int, tracking: schemas.TrackingUpdate):
    db_tracking = db.query(models.Tracking).filter(models.Tracking.id == tracking_id).first()
    if db_tracking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking not found")
    for key, value in tracking.dict(exclude_unset=True).items():
        setattr(db_tracking, key, value)
    db.commit()
    return db_tracking

def delete_tracking(db: Session, tracking_id: int):
    db_tracking = db.query(models.Tracking).filter(models.Tracking.id == tracking_id).first()
    if db_tracking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking not found")
    db.delete(db_tracking)
    db.commit()
