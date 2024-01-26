
import random
import string
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from typing import List
from datetime import datetime, timedelta
import pytz
import uuid
import os
import CRUD.course as course_crud
import CRUD.post_reaction as reaction_crud
import CRUD.post_content as post_content_crud
from redis_client import redis_client
from sqlalchemy import func
from CRUD.user import read_user_by_id

# create challenge
def create_challenge(db: Session, challenge: schemas.ChallengeCreate):
    db_challenge = models.Challenge(
        title=challenge.title,
        description=challenge.description,
        duration=challenge.duration,
        breaking_days=challenge.breaking_days,
        is_public=challenge.is_public,
        category=challenge.category,
        cover_location=challenge.cover_location,
        challenge_owner_id=challenge.challenge_owner_id,
        course_id=None,
        is_completed=None,
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)

    db_group_challenge = models.GroupChallengeMembers(
        challenge_id=db_challenge.id, 
        user_id=db_challenge.challenge_owner_id, 
        breaking_days_left=db_challenge.breaking_days,  # Assuming this field exists in your ChallengeCreate schema
        is_challenge_finished=False,
        days_left=db_challenge.duration,
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

def update_breaking_days_for_challenges(db: Session):
    # 获取今天的日期字符串
    today_str = datetime.now().strftime('%Y-%m-%d')
    redis_key = f"posted_challenges:{today_str}"

    # 获取 Redis 中存储的今天已发布帖子的挑战ID和用户ID组合
    posted_combinations = {combo.decode('utf-8') for combo in redis_client.smembers(redis_key)}

    # 指定的挑战ID列表
    specific_challenge_ids = [10007, 10022, 10025, 10004]

    for challenge_id in specific_challenge_ids:
        group_challenge_members = db.query(models.GroupChallengeMembers).filter(
            models.GroupChallengeMembers.challenge_id == challenge_id
        ).all()

        for group_member in group_challenge_members:
            # 生成组合键，用于检查是否存在于 Redis 中
            combo_key = f"{challenge_id}_{group_member.user_id}"

            # 如果组合键不在 Redis 集合中，则减少 breaking_days_left
            if combo_key not in posted_combinations:
                if group_member.breaking_days_left > 0:
                    group_member.breaking_days_left -= 1

                # 如果 breaking_days_left 为0，则标记挑战为完成
                if group_member.breaking_days_left == 0:
                    challenge_to_finish = db.query(models.Challenge).filter_by(id=challenge_id).first()
                    if challenge_to_finish and not challenge_to_finish.is_completed:
                        challenge_to_finish.is_completed = True
                        challenge_to_finish.finished_time = datetime.now()

    # 提交所有更改到数据库
    db.commit()



# read all challenges
def get_challenges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Challenge).offset(skip).limit(limit).all()

# read active challenges list of one user by user id
def get_active_challenges_by_user_id(db: Session, user_id: int) -> List[schemas.ChallengeWithBreakingDays]:
    results = (
        db.query(models.Challenge, models.GroupChallengeMembers)
        .join(models.GroupChallengeMembers, models.GroupChallengeMembers.challenge_id == models.Challenge.id)
        .filter(models.Challenge.challenge_owner_id == user_id, models.Challenge.finished_time == None)
        .all()
    )
    # Create ChallengeWithBreakingDays instances from the results
    active_challenges = []
    for challenge, group_challenge_members in results:
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
            is_completed=challenge.is_completed,
            days_left=group_challenge_members.days_left,
            is_group_challenge=challenge.is_group_challenge,
            breaking_days_left=group_challenge_members.breaking_days_left  # Access the attribute from group_member
        )
        active_challenges.append(challenge_data)
    
    return active_challenges

# read finished challenges list of one user by user id
def get_finished_challenges_by_user_id(db: Session, user_id: int) -> List[schemas.ChallengeWithBreakingDays]:
    results = (
        db.query(models.Challenge, models.GroupChallengeMembers)
        .join(models.GroupChallengeMembers, models.GroupChallengeMembers.challenge_id == models.Challenge.id)
        .filter(models.Challenge.challenge_owner_id == user_id, models.Challenge.finished_time != None)
        .all()
    )
    # Create ChallengeWithBreakingDays instances from the results
    finished_challenges = []
    for challenge, group_challenge_members in results:
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
            is_completed=challenge.is_completed,
            days_left=group_challenge_members.days_left,
            is_group_challenge=challenge.is_group_challenge,
            breaking_days_left=group_challenge_members.breaking_days_left  # Access the attribute from group_member
        )
        finished_challenges.append(challenge_data)
    
    return finished_challenges

# read challenges list by course id
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
        return False
    db.delete(db_challenge)
    db.commit()
    return True

# 中途退出group challenge
def delete_group_challenge_member(db: Session, challenge_id: int, user_id: int):
    db_group_challenge_member = db.query(models.GroupChallengeMembers).filter(models.GroupChallengeMembers.challenge_id == challenge_id).filter(models.GroupChallengeMembers.user_id == user_id).first()
    if db_group_challenge_member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    db.delete(db_group_challenge_member)
    db.commit()


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
def get_challenge_process(duration, days_left):
    challenge_process = days_left / duration
    return challenge_process
#用challenge_id拿到discover challenge的详细信息
def get_discover_challenges_by_id(db: Session, id: int):
    challenge_query_result = db.query(models.Challenge, models.GroupChallengeMembers, models.User).join(models.User, models.Challenge.challenge_owner_id == models.User.id).join(
            models.GroupChallengeMembers, models.Challenge.id == models.GroupChallengeMembers.challenge_id).filter(models.Challenge.id == id).first()
    challenge_obj, group_challenge_members_obj, user_obj = challenge_query_result[0], challenge_query_result[1], challenge_query_result[2]
    challenge_process = get_challenge_process(challenge_obj.duration, group_challenge_members_obj.days_left)
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
    challenges = db.query(models.Challenge).filter(models.Challenge.finished_time != None).all()#这里可以用limit（）改成想要的数量
    for challenge in challenges:
        challenge_detail = get_discover_challenges_by_id(db, challenge.id)
        discover_challenges.append(challenge_detail)
    return discover_challenges
# update challenge & course relastionship by challenge id and course id
def update_challenge_course_id(db:Session, challenge_id: int, course_id: int):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if db_challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    if db_challenge.course_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Challenge has been already linked to course")
    db_challenge.course_id = course_id
    db.commit()
    return db_challenge

def challenge_details_page_first_half_by_challengeID(db: Session, challenge_id: int):
    challenge_basic_info = get_challenge(db, challenge_id)
    follower_avatars = get_all_follower_avatars(db, challenge_id)[0:5]
    # handle the case when course_id is None
    if challenge_basic_info.course_id is not None:
        course_title = course_crud.read_course_by_id(db, challenge_basic_info.course_id).course_name
    else:
        course_title = None
    owner_avatar = get_owner_avatar_by_user_id(db, challenge_basic_info.challenge_owner_id)
    challenge_details ={
        "id": challenge_basic_info.id,
        "title": challenge_basic_info.title,
        "DisplayName": get_name_by_user_id(db, challenge_basic_info.challenge_owner_id),
        "Username": get_userName_by_user_id(db, challenge_basic_info.challenge_owner_id),
        "Description": challenge_basic_info.description,
        "follwers_avaters": follower_avatars,
        "Course": course_title,
        "owner_avatar": owner_avatar,
        "cover_location": challenge_basic_info.cover_location,
    }
    return challenge_details

def get_userName_by_user_id(db:Session, user_id: int):
    result = db.query(models.User).filter(models.User.id == user_id).first()
    if result:
        return result.username
    else:
        return None
    
def get_name_by_user_id(db:Session, user_id: int):
    result = db.query(models.User).filter(models.User.id == user_id).first()
    if result:
        return result.name
    else:
        return None
    
def get_owner_avatar_by_user_id(db:Session, user_id: int):
    result = db.query(models.User).filter(models.User.id == user_id).first()
    if result:
        return result.avatar_location
    else:
        return None

def reformat_reaction_count_list(db:Session, post_id: int):
    db_reaction = reaction_crud.get_post_reactions_by_postid(db, post_id)
    all_reaction_count = []
    for item in db_reaction:
        each_block = {
                item.emoji_image: item.count
        }
        all_reaction_count.append(each_block)

    return all_reaction_count


def challenge_details_page_second_half_by_challengeID(db: Session, challenge_id: int):
    db_post_details = db.query(
        models.Post, models.PostContent, models.PostReaction, models.GroupChallengeMembers
    ).join(
        models.PostContent, models.PostContent.post_id == models.Post.id
    ).join(
        models.PostReaction, models.PostReaction.post_id == models.Post.id
    ).join(
        models.GroupChallengeMembers, models.GroupChallengeMembers.challenge_id == models.Post.challenge_id
    ).filter(
        models.Post.challenge_id == challenge_id
    ).all()

    grouped_posts = {}
    for item in db_post_details:
        Post_obj, PostContent_obj, PostReaction_obj, GroupChallengeMembers_obj = item
        username = get_userName_by_user_id(db, GroupChallengeMembers_obj.user_id)
        post_data = {
            "id": Post_obj.id,
            "written_text": Post_obj.written_text,
            "reactions": reformat_reaction_count_list(db, PostReaction_obj.post_id),
            "PostContent": post_content_crud.get_post_contents_by_post_id(db, PostContent_obj.post_id)
        }
        
        # Group posts by username
        if username not in grouped_posts:
            grouped_posts[username] = {
                "UserName": username,
                "Posts": [post_data]
            }
        else:
            grouped_posts[username]["Posts"].append(post_data)

    # Convert the grouped posts back to a list of dictionaries
    all_page_post_container = list(grouped_posts.values())
    return all_page_post_container

def compare_created_time_by_challenge_id(db: Session, challenge_id:int):
    target_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if target_challenge:
        target_challenge_created_time = target_challenge.created_time
        # Compare only the date part of 'created_time' with today's date
        result = target_challenge_created_time.date() == datetime.now().date()
        print(result)
        return result
    else:
        print("False")
        return False  # or handle as appropriate if the challenge is not found

def get_end_of_day_in_user_timezone(user_timezone):
    # Get the current time in UTC
    utc_now = datetime.utcnow()
    # Convert UTC to user's timezone
    user_tz = pytz.timezone(user_timezone)
    user_now = utc_now.replace(tzinfo=pytz.utc).astimezone(user_tz)
    # Calculate the end of the day in user's timezone
    end_of_day_user_tz = user_now.replace(hour=23, minute=59, second=59, microsecond=0)
    return end_of_day_user_tz


def generate_invitation_code(db : Session, challenge_id : int):
    
    unique_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    user_timezone = db.query(models.User).filter(models.User.id == models.Challenge.challenge_owner_id).first().user_timezone
    end_of_day_user_tz = get_end_of_day_in_user_timezone(user_timezone)

    if redis_client.get(challenge_id) is None and compare_created_time_by_challenge_id(db, challenge_id):
        # today = datetime.now()
        # end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59)
        # remaining_time = end_of_day - today
        remaining_time = (end_of_day_user_tz - datetime.now(pytz.utc)).total_seconds()
        redis_key = unique_token
        redis_client.set(redis_key, challenge_id)
        redis_client.set(challenge_id, redis_key)
        redis_client.expire(redis_key, int(remaining_time))
        redis_client.expire(challenge_id, int(remaining_time))
    else:
        print(redis_client.get(unique_token))
        today = datetime.now()
        print(today)
        return "Invitation link already exsist or the link has been expired."

    print(today)
    return f"invitation code:{unique_token}"

def get_challenge_category_distribution(db: Session, user_id: int):
    count_result = db.query(
        models.Challenge.category,
        func.count(models.GroupChallengeMembers.user_id)
    ).join(
        models.GroupChallengeMembers, models.GroupChallengeMembers.challenge_id == models.Challenge.id
    ).filter(
        models.GroupChallengeMembers.user_id == user_id
    ).group_by(
        models.Challenge.category
    ).all()

    total_challenge_amount = sum([count_element[1] for count_element in count_result])
    category_amounts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}  # Assuming categories are 0, 1, 2, 3, 4

    for category, amount in count_result:
        category_amounts[category] = amount

    result = [category_amounts[i] for i in range(5)]  # Assuming 5 categories
    return result

def join_group_challenge_by_token_and_user_id(db: Session, unique_token : str, user_id: str):
    
    request_challenge_id_bytes = redis_client.get(unique_token)

    if request_challenge_id_bytes is not None:
        request_challenge_id_str = request_challenge_id_bytes.decode('utf-8')  # 解码字节字符串
        request_challenge_id = int(request_challenge_id_str)  # 转换成整数
    else:
        return "Can not find the token in redis"

    request_challenge = db.query(models.Challenge).filter(models.Challenge.id == request_challenge_id).first()
    
    if request_challenge_id and db.query(models.GroupChallengeMembers).filter(models.GroupChallengeMembers.user_id == user_id).filter(models.GroupChallengeMembers.challenge_id == request_challenge_id).first() is None:
        join_group_challenge = models.GroupChallengeMembers(
                challenge_id = request_challenge_id,
                user_id = user_id,
                breaking_days_left = request_challenge.breaking_days,
                days_left = request_challenge.duration * 7
        )
        db.add(join_group_challenge)
        db.commit()
        db.refresh(join_group_challenge)
        return "New group member has joined!"
    elif request_challenge_id and db.query(models.GroupChallengeMembers).filter(models.GroupChallengeMembers.user_id == user_id).filter(models.GroupChallengeMembers.challenge_id == request_challenge_id).first():
        return "User already joined the group challenge"
    else:
        return "Can not found the challenge!"

def challenge_card_by_challengeID(db: Session, challenge_id: int):

    challenge_basic_info = get_challenge(db, challenge_id)
    follower_avatars = get_all_follower_avatars(db, challenge_id)[0:5]
    owner_avatar = get_owner_avatar_by_user_id(db, challenge_basic_info.challenge_owner_id)
    challenge_details ={
        "title": challenge_basic_info.title,
        "description": challenge_basic_info.description,
        "duration": challenge_basic_info.duration,
        "breaking_days": challenge_basic_info.breaking_days,
        "is_public": challenge_basic_info.is_public,
        "is_completed": challenge_basic_info.is_completed,
        "created_time": challenge_basic_info.created_time,
        "category": challenge_basic_info.category,
        "cover_location": challenge_basic_info.cover_location,
        "id": challenge_basic_info.id,
        "finished_time": challenge_basic_info.finished_time,
        "challenge_owner_id": challenge_basic_info.challenge_owner_id,
        "course_id": challenge_basic_info.course_id,
        "user_avatar_location": owner_avatar,
        "followers": follower_avatars,
    }
    return challenge_details
