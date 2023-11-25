
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from typing import List

# create challenge
def create_challenge(db: Session, challenge: schemas.ChallengeCreate):
    db_challenge = models.Challenge(**challenge.dict())
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

# read challenge by id
def get_challenge(db: Session, challenge_id: int):
    challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge

# read all challenges
def get_challenges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Challenge).offset(skip).limit(limit).all()

# read active challengs list of one user by user id
def get_active_challenges_by_user_id(db: Session, user_id: int) -> List[models.Challenge]:
    active_challenges = (
        db.query(models.Challenge)
        .filter(models.Challenge.user_id == user_id, models.Challenge.is_finished == False)
        .all()
    )
    return active_challenges

# read finished challenges list of one user by user id
def get_finished_challenges_by_user_id(db: Session, user_id: int) -> List[models.Challenge]:
    finished_challenges = (
        db.query(models.Challenge)
        .filter(models.Challenge.user_id == user_id, models.Challenge.is_finished == True)
        .all()
    )
    return finished_challenges

# read challengs list by course id
def get_challenges_by_course_id(db: Session, course_id: int) -> List[models.Challenge]:
    challenges_with_course_id = (
        db.query(models.Challenge)
        .filter(models.Challenge.course_id == course_id)
        .all()
    )
    return challenges_with_course_id

# read all challenges of one user by user id
# not used in router/challenge.py 
def get_user_challenges(db: Session, user_id: int):
    active_challenges = get_active_challenges_by_user_id(db, user_id)
    finished_challenges = get_finished_challenges_by_user_id(db, user_id)
    return [active_challenges, finished_challenges]

# update challenge by by challenge id
def update_challenge(db: Session, challenge_id: int, challenge: schemas.ChallengeCreate):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if db_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    for key, value in challenge.dict(exclude_unset=True).items():
        setattr(db_challenge, key, value)
    db.commit()
    return db_challenge

# delete challenge by id
def delete_challenge(db: Session, challenge_id: int):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if db_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    db.delete(db_challenge)
    db.commit()

