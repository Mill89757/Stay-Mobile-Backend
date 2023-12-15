
from sqlalchemy import desc
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from typing import List
from datetime import datetime, timedelta
import pytz

def create_challenge(db: Session, challenge: schemas.ChallengeCreate):
    db_challenge = models.Challenge(**challenge.dict())
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def get_challenge(db: Session, challenge_id: int):
    challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge

def get_challenges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Challenge).offset(skip).limit(limit).all()


def get_active_challenges_by_user_id(db: Session, user_id: int) -> List[models.Challenge]:
    active_challenges = (
        db.query(models.Challenge)
        .filter(models.Challenge.user_id == user_id, models.Challenge.is_finished == False)
        .all()
    )
    return active_challenges

def get_finished_challenges_by_user_id(db: Session, user_id: int) -> List[models.Challenge]:
    finished_challenges = (
        db.query(models.Challenge)
        .filter(models.Challenge.user_id == user_id, models.Challenge.is_finished == True)
        .all()
    )
    return finished_challenges

def get_challenges_by_course_id(db: Session, course_id: int) -> List[models.Challenge]:
    challenges_with_course_id = (
        db.query(models.Challenge)
        .filter(models.Challenge.course_id == course_id)
        .all()
    )
    return challenges_with_course_id

def get_last_challenge_by_user_id(db: Session, user_id: int):
    last_challenge = (db.query(models.Challenge)
        .filter(models.Challenge.user_id == user_id)
        .order_by(desc(models.Challenge.created_time)).first()
        )
    return last_challenge

def get_user_challenges(db: Session, user_id: int):
    active_challenges = get_active_challenges_by_user_id(db, user_id)
    finished_challenges = get_finished_challenges_by_user_id(db, user_id)
    return [active_challenges, finished_challenges]

def get_challenge_durations_by_category(db: Session, user_id: int):
    # Step 1: Filter challenges for the user
    challenges = db.query(models.Challenge).filter(models.Challenge.user_id == user_id).all()

    # Step 2: Determine the date range
    sydney_tz = pytz.timezone('Australia/Sydney')
    today = datetime.now(sydney_tz).date()
    date_range = [today - timedelta(days=i) for i in range(5)]

    # Step 3 & 4: Filter posts, group by category, and calculate durations
    durations_by_date_category = {date.strftime("%d/%m"): {} for date in date_range}

    for date in date_range:
        start_of_day = datetime.combine(date, datetime.min.time(), tzinfo=sydney_tz)
        end_of_day = datetime.combine(date, datetime.max.time(), tzinfo=sydney_tz)
        
        # Filter posts by date range and user_id
        daily_posts = db.query(models.Post, models.Challenge).join(models.Challenge).filter(
            models.Post.user_id == user_id,
            models.Post.start_time >= start_of_day,
            models.Post.end_time <= end_of_day
        ).all()

        for post, challenge in daily_posts:
            category = models.Challenge.category
            post_duration = (models.Post.end_time - models.Post.start_time).total_seconds() / 60  # duration in minutes
            
            if category not in durations_by_date_category[date.strftime("%d/%m")]:
                durations_by_date_category[date.strftime("%d/%m")][category] = 0
            durations_by_date_category[date.strftime("%d/%m")][category] += post_duration

    return durations_by_date_category

# This function should be integrated into your backend application.
# Make sure to replace 'session.query' with your actual database session or query interface.



def update_challenge(db: Session, challenge_id: int, challenge: schemas.ChallengeCreate):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if db_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    for key, value in challenge.dict(exclude_unset=True).items():
        setattr(db_challenge, key, value)
    db.commit()
    return db_challenge

def delete_challenge(db: Session, challenge_id: int):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if db_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    db.delete(db_challenge)
    db.commit()

