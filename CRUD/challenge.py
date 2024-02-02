
from pyexpat import model
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from typing import List
from datetime import datetime, timedelta
import pytz
import redis_client
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

# update challenge & course relationship by challenge id and course id
def update_challenge_course_id(db:Session, challenge_id: int, course_id: int):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if db_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    if db_challenge.course_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Challenge has been already linked to a course")
    db_challenge.course_id = course_id
    db.commit()
    return db_challenge

# check if the user is the challenge onwer or not
def check_challenge_onwer(db:Session, challenge_id:int, user_id):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if db_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    else:
        if db_challenge.challenge_owner_id == user_id:
            return True
        else:
            return False

TIMEZONE_MAPPING = {
    "Sydney": "Australia/Sydney",
    "Perth": "Australia/Perth",
    "Brisbane": "Australia/Brisbane",
    "Beijing": "Asia/Shanghai"
}
# check user activity at 12pm and 6pm
def check_user_activity(db:Session, challenge_id_list: list):
    # user_timezone = pytz.timezone(TIMEZONE_MAPPING.get(timezone_str, "UTC"))
    current_time = datetime.now()

    current_date_str = current_time.strftime('%Y-%m-%d')
    remind_user_list = []
    # 获取Redis中存储的帖子跟踪键
    redis_key = f"posted_challenges:{current_date_str}"
    posted_combinations = {combo.decode('utf-8') for combo in redis_client.smembers(redis_key)}

    for challenge_id in challenge_id_list:
        group_challenge_members = db.query(models.GroupChallengeMembers).filter(
            models.GroupChallengeMembers.challenge_id == challenge_id
        ).all()

        for group_member in group_challenge_members:
            combo_key = f"{challenge_id}_{group_member.user_id}"
            check_user_timezone = db.query(models.User).filter(models.User.id == group_member.user_id).first()

            if combo_key not in posted_combinations:
                #if check_user_timezone.user_timezone == timezone_str:
                if group_member.breaking_days_left > 0:
                    remind_user_list.append(check_user_timezone.id)
            
    return remind_user_list

