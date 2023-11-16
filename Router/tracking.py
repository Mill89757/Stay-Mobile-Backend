from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas  
from database import get_db  
import CRUD.tracking as tracking_crud  # Make sure to create this CRUD module for tracking

router = APIRouter()

@router.post("/CreateTracking/", response_model=schemas.TrackingRead, status_code=status.HTTP_201_CREATED)
async def create_tracking_route(tracking: schemas.TrackingCreate, db: Session = Depends(get_db)):
    return tracking_crud.create_tracking(db=db, tracking=tracking)

@router.get("/GetTracking/{tracking_id}", response_model=schemas.TrackingRead)
async def get_tracking_route(tracking_id: int, db: Session = Depends(get_db)):
    tracking = tracking_crud.get_tracking(db=db, tracking_id=tracking_id)
    if tracking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking not found")
    return tracking

@router.get("/GetAllTrackings/", response_model=list[schemas.TrackingRead])
async def get_trackings_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return tracking_crud.get_trackings(db=db, skip=skip, limit=limit)

@router.put("/UpdateTracking/{tracking_id}", response_model=schemas.TrackingRead)
async def update_tracking_route(tracking_id: int, tracking: schemas.TrackingUpdate, db: Session = Depends(get_db)):
    updated_tracking = tracking_crud.update_tracking(db=db, tracking_id=tracking_id, tracking=tracking)
    if updated_tracking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking not found")
    return updated_tracking

@router.delete("/DeleteTracking/{tracking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tracking_route(tracking_id: int, db: Session = Depends(get_db)):
    if not tracking_crud.delete_tracking(db=db, tracking_id=tracking_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Tracking deleted successfully"})
