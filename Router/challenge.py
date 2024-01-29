from cmath import asin
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas  
from database import get_db  
import CRUD.challenge as challenge_crud
from typing import List

# create routes for challenges operations and functions
router = APIRouter()

# create challenge
@router.post("/CreateChallenge/", response_model=schemas.ChallengeRead, status_code=status.HTTP_201_CREATED)
async def create_challenge_route(challenge: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    return challenge_crud.create_challenge(db=db, challenge=challenge)

# read chanllenge by id
@router.get("/GetChallenge/{challenge_id}", response_model=schemas.ChallengeRead)
async def get_challenge_route(challenge_id: int, db: Session = Depends(get_db)):
    challenge = challenge_crud.get_challenge(db=db, challenge_id=challenge_id)
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge

# read all challenges of one user by user id 
@router.get("/GetUserChallenges/{user_id}", response_model=List[List[schemas.ChallengeRead]])
async def get_user_challenges_route(user_id: int, db: Session = Depends(get_db)):
    active_challenges = challenge_crud.get_active_challenges_by_user_id(db, user_id)
    finished_challenges = challenge_crud.get_finished_challenges_by_user_id(db, user_id)
    return [active_challenges, finished_challenges]

# read active challenges of one user by user id
@router.get("/GetUserActiveChallenges/{user_id}", response_model=List[schemas.ChallengeRead])
async def get_user_active_challenges_route(user_id: int, db: Session = Depends(get_db)):
    active_challenges = challenge_crud.get_active_challenges_by_user_id(db, user_id)
    return active_challenges

# read challenges list by course id
@router.get("/GetChallengesWithCourseID/{course_id}", response_model=List[schemas.ChallengeRead])
async def get_challenge_courseTD(course_id: int, db: Session = Depends(get_db)):
    CourseID_related_challenges = challenge_crud.get_challenges_by_course_id(db, course_id)
    return CourseID_related_challenges

# read finished challenges list of one user by user id
@router.get("/GetUserFinishedChallenges/{user_id}", response_model=List[schemas.ChallengeRead])
async def get_user_finished_challenges_route(user_id: int, db: Session = Depends(get_db)):
    finished_challenges = challenge_crud.get_finished_challenges_by_user_id(db, user_id)
    return finished_challenges

@router.get("/GetAllChallenges/", response_model=list[schemas.ChallengeRead])
async def get_challenges_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return challenge_crud.get_challenges(db=db, skip=skip, limit=limit)

# update challenges by challenge id
@router.put("/UpdateChallenge/{challenge_id}", response_model=schemas.ChallengeRead)
async def update_challenge_route(challenge_id: int, challenge: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    updated_challenge = challenge_crud.update_challenge(db=db, challenge_id=challenge_id, challenge=challenge)
    if updated_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return updated_challenge

# delete challenges by challenge id
@router.delete("/DeleteChallenge/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge_route(challenge_id: int, db: Session = Depends(get_db)):
    if not challenge_crud.delete_challenge(db=db, challenge_id=challenge_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Challenge deleted successfully"})


# check if user is the challenge owner or not
@router.get("/CheckOwner/{challenge_id}")
async def check_challenge_owner(challenge_id: int, user_id: int, db: Session=Depends(get_db)):
    result = challenge_crud.check_challenge_onwer(challenge_id=challenge_id, user_id=user_id, db=db)
    return result