from fastapi import APIRouter, status, Depends, HTTPException
from database import SessionLocal
import schemas
import CRUD.tracking as crud
from sqlalchemy.orm import Session
from typing import List

# create routes for tracking operations and functions
router = APIRouter(
    prefix="/tracking"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create tracking
@router.post("", status_code=status.HTTP_201_CREATED)
def create_tracking(tracking: schemas.TrackingsRequest, db: Session = Depends(get_db)):
    tracking = crud.create_tracking(db, tracking)
    return tracking

# read tracking by challenge_id
@router.get("/challenge/{challenge_id}", response_model=List[schemas.TrackingsResponse])
def get_tracking_by_challenge_id(challenge_id: int, db: Session = Depends(get_db)):
    tracking = crud.read_tracking_by_challenge_id(db, challenge_id)
    if tracking is None:
        raise HTTPException(status_code=404, detail="challenge not found")
    return tracking

# update tracking status
@router.put("/")
def update_tracking_status(challenge_id: int, follower_id: int, tracking: schemas.TrackingsResponse, db: Session = Depends(get_db)):
    res = crud.update_tracking_status(db, challenge_id, follower_id, tracking)
    return res

# delete tracking by id
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_tracking(id: int, db: Session = Depends(get_db)):
    res = crud.delete_tracking(db, id)
    if res is None:
        raise HTTPException(status_code=404, detail="tracking not found")