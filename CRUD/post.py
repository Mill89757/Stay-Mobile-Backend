from typing import List
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import desc, func
import redis
from datetime import datetime, timedelta
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def create_post(db: Session, post: schemas.PostCreate):
    
    challenge = db.query(models.Challenge).filter(models.Challenge.id == post.challenge_id).first()
    current_breaking_days_left = (db.query(models.GroupChallengeMembers).filter(models.GroupChallengeMembers.challenge_id == post.challenge_id).filter(models.GroupChallengeMembers.user_id == post.user_id).first())
    if not challenge:
        return "Challenge not found"

    new_days_left = challenge.days_left - 1
    new_breaking_days_left = current_breaking_days_left.breaking_days_left - (1 if post.start_time == post.end_time else 0)

    if new_days_left < 0 or new_breaking_days_left < 0:
        return "Cannot create post as it would result in negative days left or breaking days left"

    db_post = models.Post(
        user_id=post.user_id,
        challenge_id=post.challenge_id,
        start_time=post.start_time,
        end_time=post.end_time,
        written_text=post.written_text,
    )
    db.add(db_post)
    db.commit()
    challenge.days_left = new_days_left
    current_breaking_days_left.breaking_days_left = new_breaking_days_left
    db.commit()
    db.refresh(db_post)
    today = datetime.now()
    end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59)
    remaining_time = end_of_day - today
    redis_key = f"posted_challenges:{today.strftime('%Y-%m-%d')}"
    redis_client.sadd(redis_key, post.challenge_id)
    redis_client.expire(redis_key, remaining_time.seconds)

    # 打印 Redis 
    redis_value = redis_client.smembers(redis_key)
    print(f"Redis Key: {redis_key}")
    print(f"Redis Value (challenge_ids): {redis_value}")

    db_post_content = models.PostContent(
        post_id=db_post.id,
        video_location = None,
        image_location = post.image_location,
        voice_location = None,
    )
    db.add(db_post_content)
    db.commit()
    db.refresh(db_post_content)

    return db_post

# read post by post id
def get_post(db:Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

# read all posts
def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).order_by(desc(models.Post.created_time)).offset(skip).limit(limit).all()

# read posts of one user by user id
def get_posts_by_user_id(db: Session, user_id: int) -> List[models.Post]:
    user_id_posts = (
        db.query(models.Post)
        .filter(models.Post.user_id == user_id)
        .all()
    )
    return user_id_posts

# read posts by challenge id
def get_posts_by_challenge_id(db: Session, challenge_id: int) -> List[models.Post]:
    challenge_id_posts = (
        db.query(models.Post)
        .filter(models.Post.challenge_id == challenge_id)
        .all()
    )
    return challenge_id_posts

# update post by post id
def update_post(db: Session, post_id: int, post: schemas.PostCreate):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    for key, value in post.dict(exclude_unset=True).items():
        setattr(db_post, key, value)
    db.commit()
    return db_post

# delete post by post id
def delete_post(db: Session, post_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"detail": "Post has been deleted"}

# read the recent post duration for a user
def get_duration_in_minutes(start_time, end_time):
    if start_time and end_time:
        duration = end_time - start_time
        return int(duration.total_seconds() / 60)
    return 0


from datetime import datetime, timedelta
# ... other imports

from sqlalchemy import func
# ... other imports

def get_recent_post_duration(db: Session, user_id: int):
    recent_days = 5
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=recent_days)

    query_result = db.query(models.Post, models.Challenge, models.GroupChallengeMembers)\
                        .join(models.Challenge, models.Challenge.id == models.Post.challenge_id)\
                        .join(models.GroupChallengeMembers, models.GroupChallengeMembers.challenge_id == models.Post.challenge_id)\
                        .filter(models.GroupChallengeMembers.user_id == user_id)\
                        .filter(func.date(models.Post.end_time) >= start_date, func.date(models.Post.end_time) <= end_date)\
                        .order_by(models.Post.created_time)

    dummy_duration_data = [[] for _ in range(recent_days)]
    for item in query_result:
        post_obj, challenge_obj, _ = item
        duration = get_duration_in_minutes(post_obj.start_time, post_obj.end_time)
        category = challenge_obj.category
        
        post_end_date = post_obj.end_time.date()  # Here, post_obj.end_time is a Python datetime object, so it's fine
        day_index = (end_date - post_end_date).days
        if 0 <= day_index < recent_days:
            dummy_duration_data[day_index].append({"value": duration, "category": category, "challenge id": challenge_obj.id})

    return dummy_duration_data
