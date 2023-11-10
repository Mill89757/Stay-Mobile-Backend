from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas  
from database import get_db  
import CRUD.challenge as crud


router = APIRouter()

@router.post("/", response_model=schemas.ChallengeRead, status_code=status.HTTP_201_CREATED)
async def create_challenge_route(challenge: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    return crud.create_challenge(db=db, challenge=challenge)

@router.get("/{challenge_id}", response_model=schemas.ChallengeRead)
async def get_challenge_route(challenge_id: int, db: Session = Depends(get_db)):
    challenge = crud.get_challenge(db=db, challenge_id=challenge_id)
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge

@router.get("/", response_model=list[schemas.ChallengeRead])
async def get_challenges_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_challenges(db=db, skip=skip, limit=limit)

@router.put("/{challenge_id}", response_model=schemas.ChallengeRead)
async def update_challenge_route(challenge_id: int, challenge: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    updated_challenge = crud.update_challenge(db=db, challenge_id=challenge_id, challenge=challenge)
    if updated_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return updated_challenge

@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge_route(challenge_id: int, db: Session = Depends(get_db)):
    if not crud.delete_challenge(db=db, challenge_id=challenge_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return {"detail": "Challenge deleted successfully"}
