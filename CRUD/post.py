from typing import List
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import desc, func
import redis
from datetime import datetime, timedelta
from CRUD.user import read_user_by_id
from redis_client import redis_client


def create_post(db: Session, post: schemas.PostCreate):
    challenge = db.query(models.Challenge).filter(models.Challenge.id == post.challenge_id).first()
    current_challenge_member_DL_and_BDL = (db.query(models.GroupChallengeMembers).filter(models.GroupChallengeMembers.challenge_id == post.challenge_id).filter(models.GroupChallengeMembers.user_id == post.user_id).first())
    if not challenge:
        return "Cannot create post, Challenge not found"

    new_days_left = current_challenge_member_DL_and_BDL.days_left - 1
    new_breaking_days_left = current_challenge_member_DL_and_BDL.breaking_days_left - (1 if post.start_time == post.end_time else 0)

    if new_days_left < 0 or new_breaking_days_left < 0:
        return "Cannot create post as it would result in negative days left or breaking days left"
    
    def create_post_action(db: Session, post: schemas.PostCreate):
        db_post = models.Post(
            user_id=post.user_id,
            challenge_id=post.challenge_id,
            start_time=post.start_time,
            end_time=post.end_time,
            written_text=post.written_text,
        )
        db.add(db_post)
        db.commit()
        current_challenge_member_DL_and_BDL.days_left = new_days_left
        current_challenge_member_DL_and_BDL.breaking_days_left = new_breaking_days_left
        db.commit()
        db.refresh(db_post)
        # 生成唯一组合键和当天的帖子跟踪键
        today = datetime.now()
        end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59)
        remaining_time = end_of_day - today
        today_str = datetime.now().strftime('%Y-%m-%d')
        unique_key = f"challenge_user:{post.challenge_id}_{post.user_id}_{today_str}"
        daily_key = f"posted_challenges:{today_str}"

        # 将唯一组合键添加到 Redis 并设置过期时间
        redis_client.set(unique_key, 'posted')
        redis_client.expire(unique_key, remaining_time.seconds)

        # 同时将挑战ID和用户ID组合作为值添加到当天的帖子跟踪键中
        redis_client.sadd(daily_key, f"{post.challenge_id}_{post.user_id}")
        redis_client.expire(daily_key, remaining_time.seconds)

        # 打印 Redis
        print(f"Redis Key: {unique_key} and {daily_key}")
        print(f"Redis Values: {redis_client.get(unique_key)}, {redis_client.smembers(daily_key)}")


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

    if current_challenge_member_DL_and_BDL.days_left > 1 and challenge.is_completed is False:
        result = create_post_action(db, post)
        return result
    elif current_challenge_member_DL_and_BDL.days_left == 1:
        if challenge.is_group_challenge is False:
            result = create_post_action(db, post)
            challenge.is_completed = True
            current_challenge_member_DL_and_BDL.is_challenge_finished = True
            challenge.finished_time = post.end_time
            db.commit()
            return result
        elif challenge.is_group_challenge is True:
            result = create_post_action(db, post)
            current_challenge_member_DL_and_BDL.is_challenge_finished = True
            other_group_members = db.query(models.GroupChallengeMembers).filter(models.GroupChallengeMembers.challenge_id == post.challenge_id).all() 
            all_finished = all(member.is_challenge_finished for member in other_group_members)
            if all_finished:
                challenge.is_completed = True
                challenge.finished_time = post.end_time
                db.commit()
                return result
    else:
        return "Cannot create post, no days left for the challenge"
    

# read post by post id
def get_post(db:Session, post_id: int):
    """ Return the post by post id
    
    Args:
        post_id (int): post id
    
    Returns:
        post: post object    

    Raises:
        HTTPException: post not found
    """
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

# read all posts
def get_posts(db: Session, skip: int = 0, limit: int = 100):
    """ Return all posts
    
    Args:
        skip (int): skip
        limit (int): limit
    
    Returns:
        list of posts object
    """
    posts = db.query(models.Post, models.Challenge).join(models.Challenge, models.Challenge.id == models.Post.challenge_id).order_by(desc(models.Post.created_time)).filter(models.Challenge.is_public == True).filter(models.Post.written_text != "I have a break today!").offset(skip).limit(limit).all()
    
    final_post_list =[]

    for post_obj, challenge_obj in posts:

        post_unit = {
            "created_time": post_obj.created_time,
            "start_time": post_obj.start_time,
            "end_time": post_obj.end_time,
            "written_text": post_obj.written_text,
            "id": post_obj.id,
            "user_id": post_obj.user_id,
            "challenge_id": post_obj.challenge_id
        }

        final_post_list.append(post_unit)

    return final_post_list


def get_posts_by_ids(db: Session, post_ids: list, skip: int = 0, limit: int = 100):
    """ Return posts by their IDs
    
    Args:
        db (Session): Database session
        post_ids (list): List of post IDs to fetch
        skip (int): Number of records to skip
        limit (int): Maximum number of records to fetch
    
    Returns:
        list of post objects
    """
    posts = db.query(models.Post) \
              .filter(models.Post.id.in_(post_ids)) \
              .filter(models.Post.written_text != "I have a break today!") \
              .order_by(desc(models.Post.created_time)) \
              .offset(skip) \
              .limit(limit) \
              .all()
    return posts


# read posts of one user by user id
def get_posts_by_user_id(db: Session, user_id: int) -> List[models.Post]:
    """ Return the post by user id
    
    Args:
        user_id (int): user id
    
    Returns:
        post: post object
        
    Raises:
        HTTPException: post not found
        HTTPException: user not found
    """
    read_user_by_id(db, user_id)#handle user not found
    user_id_posts = (
        db.query(models.Post)
        .filter(models.Post.user_id == user_id)
        .all()
    )
    return user_id_posts

# read posts by challenge id
def get_posts_by_challenge_id(db: Session, challenge_id: int) -> List[models.Post]:
    """ Return the post by challenge id

    Args:
        challenge_id (int): challenge id

    Returns:
        post: post object
    
    Raises:
        HTTPException: post not found
        HTTPException: challenge not found
    """
    challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
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


def get_recent_post_duration(db: Session, user_id: int):
    """ Return the duration of posts in the last 5 days for a user
    
    Notes: the challenge id is added for testing otherwise is hard to locate the specific post

    raise HTTPException: user not found
    """
    read_user_by_id(db, user_id)#handle user not found
    RECENT_DAYS = 5
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=RECENT_DAYS)

    query_result = db.query(models.Post, models.Challenge, models.GroupChallengeMembers)\
                        .join(models.Challenge, models.Challenge.id == models.Post.challenge_id)\
                        .join(models.GroupChallengeMembers, models.GroupChallengeMembers.challenge_id == models.Post.challenge_id)\
                        .filter(models.GroupChallengeMembers.user_id == user_id)\
                        .filter(func.date(models.Post.end_time) >= start_date, func.date(models.Post.end_time) <= end_date)\
                        .order_by(models.Post.created_time)

    duration_data = [[] for _ in range(RECENT_DAYS)]
    for item in query_result:
        post_obj, challenge_obj, _ = item
        duration = get_duration_in_minutes(post_obj.start_time, post_obj.end_time)
        category = challenge_obj.category
        
        post_end_date = post_obj.end_time.date()  
        day_index = (end_date - post_end_date).days
        if 0 <= day_index < RECENT_DAYS:
            duration_data[day_index].append({"value": duration, "category": category, "challenge id": challenge_obj.id})
    
    duration_data.reverse()
    return duration_data