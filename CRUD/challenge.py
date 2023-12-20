
from sqlalchemy import desc
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from typing import List
from datetime import datetime, timedelta
import pytz

# create challenge
def create_challenge(db: Session, challenge: schemas.ChallengeCreate):
    db_challenge = models.Challenge(**challenge.dict())
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)

    db_groupchallenge = models.GroupChallengeMembers(
        challenge_id=db_challenge.id, 
        user_id=db_challenge.challenge_owner_id, 
        breaking_days_left=db_challenge.breaking_days  # Assuming this field exists in your ChallengeCreate schema
    )
    db.add(db_groupchallenge)
    db.commit()
    db.refresh(db_groupchallenge)

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
        .filter(models.Challenge.challenge_owner_id == user_id, models.Challenge.is_finished == False)
        .all()
    )
    return active_challenges

# read finished challenges list of one user by user id
def get_finished_challenges_by_user_id(db: Session, user_id: int) -> List[models.Challenge]:
    finished_challenges = (
        db.query(models.Challenge)
        .filter(models.Challenge.challenge_owner_id == user_id, models.Challenge.is_finished == True)
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

def get_last_challenge_by_user_id(db: Session, user_id: int):
    last_challenge = (db.query(models.Challenge)
        .filter(models.Challenge.challenge_owner_id == user_id)
        .order_by(desc(models.Challenge.created_time)).first()
        )
    return last_challenge

def get_challenge_breaking_days_left(db: Session, user_id: int, challenge_id):
    challenge_breaking_days_left = (db.query(models.GroupChallengeMembers)
                                    .filter(models.GroupChallengeMembers.
                                            challenge_id == challenge_id, 
                                            models.GroupChallengeMembers.user_id == user_id).first())
    return challenge_breaking_days_left

# read all challenges of one user by user id
# not used in router/challenge.py 
def get_user_challenges(db: Session, user_id: int):
    active_challenges = get_active_challenges_by_user_id(db, user_id)
    finished_challenges = get_finished_challenges_by_user_id(db, user_id)
    return [active_challenges, finished_challenges]


def get_challenge_durations_by_category(db: Session, user_id: int):
    # 查询有帖子记录的独特日期，并按降序排列
    unique_dates = db.query(models.Post.start_time).filter(models.Post.user_id == user_id)\
                      .order_by(models.Post.start_time.desc()).distinct().all()

    # 提取日期并获取最近五个独特日期
    unique_dates = [date[0].date() for date in unique_dates][:5]

    sydney_tz = pytz.timezone('Australia/Sydney')
    durations_by_date_category = {}

    for date in unique_dates:
        start_of_day = datetime.combine(date, datetime.min.time(), tzinfo=sydney_tz)
        end_of_day = datetime.combine(date, datetime.max.time(), tzinfo=sydney_tz)

        # 为这个日期初始化字典
        date_str = date.strftime("%d/%m")
        durations_by_date_category[date_str] = {}

        # 根据这个日期和user_id过滤帖子
        daily_posts = db.query(models.Post, models.Challenge).join(models.Challenge).filter(
            models.Post.user_id == user_id,
            models.Post.start_time >= start_of_day,
            models.Post.end_time <= end_of_day
        ).all()

        # 为这个日期计算每个类别的持续时间
        for post, challenge in daily_posts:
            category = challenge.category
            post_duration = (post.end_time.astimezone(sydney_tz) - post.start_time.astimezone(sydney_tz)).total_seconds() / 60
            
            if category not in durations_by_date_category[date_str]:
                durations_by_date_category[date_str][category] = 0
            durations_by_date_category[date_str][category] += post_duration

    return durations_by_date_category



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

