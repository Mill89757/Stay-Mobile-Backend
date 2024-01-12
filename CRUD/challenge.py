
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
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

    db_group_challenge = models.GroupChallengeMembers(
        challenge_id=db_challenge.id, 
        user_id=db_challenge.challenge_owner_id, 
        breaking_days_left=db_challenge.breaking_days  # Assuming this field exists in your ChallengeCreate schema
    )
    db.add(db_group_challenge)
    db.commit()
    db.refresh(db_group_challenge)

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
def get_active_challenges_by_user_id(db: Session, user_id: int) -> List[schemas.ChallengeWithBreakingDays]:
    results = (
        db.query(models.Challenge, models.GroupChallengeMembers.breaking_days_left)
        .join(models.GroupChallengeMembers, models.GroupChallengeMembers.challenge_id == models.Challenge.id)
        .filter(models.Challenge.challenge_owner_id == user_id, models.Challenge.is_finished == False)
        .all()
    )
    # Create ChallengeWithBreakingDays instances from the results
    active_challenges = []
    for challenge, breaking_days_left in results:
        challenge_data = schemas.ChallengeWithBreakingDays(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            duration=challenge.duration,
            breaking_days=challenge.breaking_days,
            is_public=challenge.is_public,
            category=challenge.category,
            created_time=challenge.created_time,
            finished_time=challenge.finished_time,
            cover_location=challenge.cover_location,
            challenge_owner_id=challenge.challenge_owner_id,
            course_id=challenge.course_id,
            is_finished=challenge.is_finished,
            days_left=challenge.days_left,
            is_group_challenge=challenge.is_group_challenge,
            breaking_days_left=breaking_days_left  # Access the attribute from group_member
        )
        active_challenges.append(challenge_data)
    
    return active_challenges

# read finished challenges list of one user by user id
def get_finished_challenges_by_user_id(db: Session, user_id: int) -> List[schemas.ChallengeWithBreakingDays]:
    results = (
        db.query(models.Challenge, models.GroupChallengeMembers.breaking_days_left)
        .join(models.GroupChallengeMembers, models.GroupChallengeMembers.challenge_id == models.Challenge.id)
        .filter(models.Challenge.challenge_owner_id == user_id, models.Challenge.is_finished == True)
        .all()
    )
    # Create ChallengeWithBreakingDays instances from the results
    finished_challenges = []
    for challenge, breaking_days_left in results:
        challenge_data = schemas.ChallengeWithBreakingDays(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            duration=challenge.duration,
            is_public=challenge.is_public,
            category=challenge.category,
            created_time=challenge.created_time,
            finished_time=challenge.finished_time,
            cover_location=challenge.cover_location,
            challenge_owner_id=challenge.challenge_owner_id,
            course_id=challenge.course_id,
            is_finished=challenge.is_finished,
            days_left=challenge.days_left,
            is_group_challenge=challenge.is_group_challenge,
            breaking_days_left=breaking_days_left  # Access the attribute from group_member
        )
        finished_challenges.append(challenge_data)
    
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
    # Step 1: Filter challenges for the user
    challenges = db.query(models.Challenge).filter(models.Challenge.challenge_owner_id == user_id).all()

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
            category = challenge.category
            post_duration = (post.end_time - post.start_time).total_seconds() / 60  # duration in minutes
            
            if category not in durations_by_date_category[date.strftime("%d/%m")]:
                durations_by_date_category[date.strftime("%d/%m")][category] = 0
            durations_by_date_category[date.strftime("%d/%m")][category] += post_duration
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

# 中途退出group challenge
def delete_group_challenge_member(db: Session, challenge_id: int, user_id: int):
    db_group_challenge_member = db.query(models.GroupChallengeMembers).filter(models.GroupChallengeMembers.challenge_id == challenge_id).filter(models.GroupChallengeMembers.user_id == user_id).first()
    if db_group_challenge_member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    db.delete(db_group_challenge_member)
    db.commit()


from CRUD.user import read_user_by_id
#拿到所有follower的头像
def get_all_follower_avatars(db: Session, challenge_id: int):
    tracking_objects = (db.query(models.Challenge, models.Tracking)
                        .join(models.Tracking, models.Tracking.challenge_id == models.Challenge.id)
                        .filter(models.Challenge.id == challenge_id)
                        .all())
    all_follower_ids = [tracking_object[1].follower_id for tracking_object in tracking_objects]
    all_follower_avatars = []
    for i in all_follower_ids:
        all_follower_avatars.append(read_user_by_id(db, i).avatar_location)
    return all_follower_avatars
#拿到challenge的进度
def get_challenge_process(duration, breaking_day_left, days_left):
    challenge_process = (duration - (breaking_day_left + days_left)) / duration
    return challenge_process
#用challenge_id拿到discover challenge的详细信息
def get_discover_challenges_by_id(db: Session, id: int):
    challenge_query_result = db.query(models.Challenge, models.GroupChallengeMembers, models.User).join(models.User, models.Challenge.challenge_owner_id == models.User.id).join(
            models.GroupChallengeMembers, models.Challenge.id == models.GroupChallengeMembers.challenge_id).filter(models.Challenge.id == id).first()
    challenge_obj, group_challenge_members_obj, user_obj = challenge_query_result[0], challenge_query_result[1], challenge_query_result[2]
    challenge_process = get_challenge_process(challenge_obj.duration,group_challenge_members_obj.breaking_days_left, challenge_obj.days_left)
    follower_avatars = get_all_follower_avatars(db, challenge_obj.id)
    challenge_detail = {"id": challenge_obj.id,
                        "title": challenge_obj.title,
                        "cover_location": challenge_obj.cover_location,
                        "owner_id": user_obj.id,
                        "owner_avatar": user_obj.avatar_location,
                        "follow_avatars": follower_avatars,
                        "challenge_process": challenge_process,
                                 }
    return challenge_detail

#返回一个list，包含所有discover challenge的详细信息
def get_discover_challenges(db: Session):
    discover_challenges = []
    challenges = db.query(models.Challenge).filter(models.Challenge.is_finished == False).all()#这里可以用limit（）改成想要的数量
    for challenge in challenges:
        challenge_detail = get_discover_challenges_by_id(db, challenge.id)
        discover_challenges.append(challenge_detail)
    return discover_challenges
