from datetime import datetime, timedelta
from typing import List

import pytz
from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

import CRUD.blocked_user_list as block_crud
import models
import schemas
from CRUD.user import read_user_by_id
from redis_client import redis_client


def create_post(db: Session, post: schemas.PostCreate):
    """ Create post """

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
        # Generate a unique key combination and a post tracking key for the day
        today = location_datetime
        end_of_day = datetime(today.year, today.month,
                              today.day, 23, 59, 59, tzinfo=today.tzinfo)
        remaining_time = (end_of_day - today) + timedelta(minutes=10)
        today_str = today.strftime('%Y-%m-%d')
        unique_key = f"challenge_user:{post.challenge_id}_{post.user_id}_{today_str}"
        daily_key = f"posted_challenges:{today_str}"

        # Add a unique composite key to Redis and set an expiration time
        redis_client.set(unique_key, 'posted')
        redis_client.expire(unique_key, remaining_time.seconds)

        # Also add the challenge ID and user ID combination as a value to the day's post tracking key
        redis_client.sadd(daily_key, f"{post.challenge_id}_{post.user_id}")
        redis_client.expire(daily_key, remaining_time.seconds)

        # Print Redis
        print(f"Redis Key: {unique_key} and {daily_key}")
        print(
            f"Redis Values: {redis_client.get(unique_key)}, {redis_client.smembers(daily_key)}")

        db_post_content = models.PostContent(
            post_id=db_post.id,
            video_location=None,
            image_location=post.image_location,
            voice_location=None,
        )
        db.add(db_post_content)
        db.commit()
        db.refresh(db_post_content)

        return db_post

    challenge = db.query(models.Challenge).filter(
        models.Challenge.id == post.challenge_id).first()
    current_challenge_member_DL_and_BDL = (
        db.query(models.GroupChallengeMembers)
        .filter(models.GroupChallengeMembers.challenge_id == post.challenge_id)
        .filter(models.GroupChallengeMembers.user_id == post.user_id).first())

    user_timezone = get_user_timezone_by_user_id(db, post.user_id)
    location_date = datetime.now().astimezone(pytz.timezone(user_timezone)).date()
    location_datetime = datetime.now().astimezone(pytz.timezone(user_timezone))

    blocked_user_list = block_crud.get_blocked_user_list(
        db=db, blocker_user_id=post.user_id)

    latest_posts = get_posts_by_challenge_id(
        db, challenge_id=post.challenge_id, blocked_user_list=blocked_user_list)
    latest_post_date = latest_posts[0].created_time.astimezone(
        pytz.timezone(user_timezone)).date()

    if latest_posts and latest_post_date == location_date:
        return "Cannot create post, you has post today!"

    if not challenge:
        return "Cannot create post, Challenge not found"

    new_days_left = current_challenge_member_DL_and_BDL.days_left - 1
    new_breaking_days_left = current_challenge_member_DL_and_BDL.breaking_days_left - \
        (1 if post.start_time == post.end_time else 0)

    if new_days_left < 0 or new_breaking_days_left < 0:
        return "Cannot create post as it would result in negative days left or breaking days left"

    if challenge.is_completed or challenge.finished_time is not None:
        return "The challenge has finished or completed"

    if current_challenge_member_DL_and_BDL.days_left > 1 and challenge.is_completed is False:
        result = create_post_action(db, post)
        return result

    if current_challenge_member_DL_and_BDL.days_left == 1:
        if challenge.is_group_challenge is False:
            result = create_post_action(db, post)
            challenge.is_completed = True
            current_challenge_member_DL_and_BDL.is_challenge_finished = True
            challenge.finished_time = post.end_time
            db.commit()
            return result
        if challenge.is_group_challenge is True:
            result = create_post_action(db, post)
            current_challenge_member_DL_and_BDL.is_challenge_finished = True
            other_group_members = db.query(models.GroupChallengeMembers).filter(
                models.GroupChallengeMembers.challenge_id == post.challenge_id).all()
            all_finished = all(
                member.is_challenge_finished for member in other_group_members)
            if all_finished:
                challenge.is_completed = True
                challenge.finished_time = post.end_time
                db.commit()
                return result
    else:
        return "Cannot create post, no days left for the challenge"


def get_user_timezone_by_user_id(db: Session, user_id: int):
    """ Read challenges list by course id

    Args:
        course_id: id of course

    Returns:
        challenges_with_course_id: list of challenges

    Raises:
        HTTPException: Course not found
    """
    user_timezone_with_course_id = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first().user_timezone
    )
    return user_timezone_with_course_id


def get_post(db: Session, post_id: int):
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


def get_posts(db: Session,  blocked_user_list: List, skip: int = 0, limit: int = 100,):
    """ Return all posts

    Args:
        skip (int): skip
        limit (int): limit

    Returns:
        list of posts object
    """
    posts = db.query(models.Post, models.Challenge, models.User)\
        .join(models.Challenge, models.Challenge.id == models.Post.challenge_id)\
        .join(models.User, models.User.id == models.Challenge.challenge_owner_id)\
        .order_by(desc(models.Post.created_time)).filter(models.Challenge.is_public)\
        .filter(models.Post.written_text != "I have a break today!")\
        .filter(not models.User.is_blocked).offset(skip).limit(limit).all()

    final_post_list = []

    for post_obj, _, _ in posts:
        # check if post is in current user's blocked user list
        if post_obj.user_id not in blocked_user_list:
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
    read_user_by_id(db, user_id)  # handle user not found
    user_id_posts = (
        db.query(models.Post)
        .filter(models.Post.user_id == user_id)
        .all()
    )
    return user_id_posts


def get_posts_by_challenge_id(
        db: Session, challenge_id: int, blocked_user_list: List) -> List[models.Post]:
    """ Return the post by challenge id

    Args:
        challenge_id (int): challenge id

    Returns:
        post: post object

    Raises:
        HTTPException: post not found
        HTTPException: challenge not found
    """
    challenge = db.query(models.Challenge).filter(
        models.Challenge.id == challenge_id).first()
    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    final_post_list = []
    challenge_id_posts = (
        db.query(models.Post)
        .filter(models.Post.challenge_id == challenge_id).order_by(desc(models.Post.created_time))
        .all()
    )
    for post_obj in challenge_id_posts:
        if post_obj.user_id not in blocked_user_list:
            final_post_list.append(post_obj)
    return final_post_list


def update_post(db: Session, post_id: int, post: schemas.PostCreate):
    """ Update post by post id """
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    for key, value in post.dict(exclude_unset=True).items():
        setattr(db_post, key, value)
    db.commit()
    return db_post


def delete_post(db: Session, post_id: int):
    """ Delete post by post id """
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"detail": "Post has been deleted"}


def get_duration_in_minutes(start_time, end_time):
    """ Return the duration in minutes between start and end time """
    if start_time and end_time:
        duration = end_time - start_time
        return int(duration.total_seconds() / 60)
    return 0


def get_recent_post_duration(db: Session, user_id: int):
    """ Return the duration of posts in the last 5 days for a user

    Notes: the challenge id is added for testing otherwise is hard to locate the specific post

    raise HTTPException: user not found
    """
    read_user_by_id(db, user_id)  # handle user not found
    RECENT_DAYS = 5
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=RECENT_DAYS)

    query_result = db.query(models.Post, models.Challenge, models.GroupChallengeMembers)\
        .join(models.Challenge, models.Challenge.id == models.Post.challenge_id)\
        .join(models.GroupChallengeMembers,
              models.GroupChallengeMembers.challenge_id == models.Post.challenge_id)\
        .filter(models.GroupChallengeMembers.user_id == user_id)\
        .filter(func.date(models.Post.end_time) >= start_date,
                func.date(models.Post.end_time) <= end_date)\
        .order_by(models.Post.created_time)

    duration_data = [[] for _ in range(RECENT_DAYS)]
    for item in query_result:
        post_obj, challenge_obj, _ = item
        duration = get_duration_in_minutes(
            post_obj.start_time, post_obj.end_time)
        category = challenge_obj.category

        post_end_date = post_obj.end_time.date()
        day_index = (end_date - post_end_date).days
        if 0 <= day_index < RECENT_DAYS:
            duration_data[day_index].append(
                {"value": duration, "category": category, "challenge id": challenge_obj.id})

    duration_data.reverse()
    return duration_data
