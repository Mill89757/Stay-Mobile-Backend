# pylint: disable=unused-argument

import os
import random
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import CRUD.blocked_user_list as block_crud
import CRUD.post as post_crud
import schemas
from auth_dependencies import conditional_depends, verify_token
from CRUD.user import read_user_by_id
from database import get_db
from r1_automation import byte_to_utf8
from redis_client import r

router = APIRouter()
REPORT_FILE_PATH = "report_content.csv"


def top3categories(user_id: int) -> set:
    """
        The 'user_contribution' key in redis is a hash table
        that record user's contribution to each challenge
        category.This function takes user_id as input and return 3
        categories where the user has spent the most time contributing.
    """
    # retrive user's challenge contribution data.
    contribution = byte_to_utf8(r.hget(
        'user_contribution', user_id), str_split_symbol=',', error_result=['0']*5)
    contribution = [int(num) for num in contribution]
    top_categories = []

    for category in range(5):

        # if user did not contribute to category i, then move on to the next category
        if contribution[category] == 0:
            continue
        # otherwise, see if user's contribution is one of the top 3 categories.
        inserted = False
        for i, top_category in enumerate(top_categories):
            if contribution[category] > contribution[top_category]:
                top_categories.insert(i, category)
                inserted = True
                break
        if not inserted and len(top_categories) < 3:
            top_categories.append(category)

        elif len(top_categories) > 3:
            contribution.pop()

    # if user contributed to less than 3 categories,
    # then randomly pick some other categories for this user
    n = len(top_categories)
    if n == 3:
        return top_categories
    other_categories = [item for item in [
        0, 1, 2, 3, 4] if item not in top_categories]
    return top_categories + random.sample(other_categories, 3-n)


def filtered_posts_from_reacted_challenges(user_id: int) -> list:
    """
        user can interact with posts, each post belongs to 1 challenge.
        so reacting to recent post is equivalent to react to a challenge.
        this function allocates new posts to users based on their interacted challenges.
    """
    post_pool = []
    recent_posts = r.hkeys('post_clg_pair')
    recent_posts = random.sample(recent_posts, min(len(recent_posts), 200))
    top3 = top3categories(user_id)

    for post_id in recent_posts:
        clg_id = r.hget('post_clg_pair', post_id)
        category = int(byte_to_utf8(r.hget(
            'on_clg_info', clg_id), str_split_symbol=',')[0])
        if category not in top3:
            interacted_post = r.sismember(
                f'{user_id}_liked_posts', post_id)
            interacted_clg = r.zscore(
                f'{user_id}_clgs_preference', post_id)
            if not interacted_post or interacted_clg:
                post_pool.append(int(byte_to_utf8(post_id)))

    return post_pool


def filtered_posts_from_top3_categories(user_id: int) -> list:
    """ 
        Retrieve posts from the top 3 categories where the 
        user has spent the most time contributing 
    """
    top3 = top3categories(user_id)
    post_pool = []

    for category_code in top3:

        # get all recent post from specified category
        raw_post_pool = r.zrangebyscore(
            f'recent_posts_for_category{category_code}', 0, float('inf'))
        raw_post_pool = [int(post) for post in raw_post_pool]
        raw_post_pool = random.sample(
            raw_post_pool, min(len(raw_post_pool), 100))

        for post_id in raw_post_pool:
            if not r.sismember(f'{user_id}_liked_posts', post_id):
                post_pool.append(post_id)

    return post_pool


def get_recommended_post(user_id):
    """ Generate a list of recommended posts for a user """
    return filtered_posts_from_reacted_challenges(user_id) + \
        filtered_posts_from_top3_categories(user_id)


@router.post("/CreatePost/",
             response_model=schemas.PostRead, status_code=status.HTTP_201_CREATED)
async def create_post_router(
        post: schemas.PostCreate, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Create a new post """
    result = post_crud.create_post(db=db, post=post)
    if isinstance(result, str) and "Cannot create post" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=result)
    return result


@router.get("/GetPost/{post_id}", response_model=schemas.PostRead)
async def get_post_route(
        post_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the post by post id

    Args:
        post_id (int): post id

    Returns:
        post: post object

    Raises:
        HTTPException: post not found
    """
    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post


@router.get("/GetPostByUserID/{user_id}", response_model=List[schemas.PostRead])
async def get_post_route_user_id(
        user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the post by user id

    Args:
        user_id (int): user id

    Returns:
        post: post object

    Raises:
        HTTPException: post not found
        HTTPException: user not found
    """
    post = post_crud.get_posts_by_user_id(db=db, user_id=user_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post


@router.get("/GetPostByChallengeID/{challenge_id}/{user_id}", response_model=List[schemas.PostRead])
async def get_post_route_challenge_id(
        challenge_id: int, user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the post by challenge id

    Args:
        challenge_id (int): challenge id

    Returns:
        post: post object

    Raises:
        HTTPException: post not found
        HTTPException: challenge not found
    """
    blocked_user_list = block_crud.get_blocked_user_list(
        db=db, blocker_user_id=user_id)
    post = post_crud.get_posts_by_challenge_id(
        db=db, challenge_id=challenge_id, blocked_user_list=blocked_user_list)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

    return post


@router.get("/GetAllposts/{user_id}", response_model=list[schemas.PostRead])
async def get_posts_route(
        user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Return all posts

    Args:
        skip (int): skip
        limit (int): limit

    Returns:
        list of posts object
    """
    blocked_user_list = block_crud.get_blocked_user_list(
        db=db, blocker_user_id=user_id)
    return post_crud.get_posts(db=db, blocked_user_list=blocked_user_list, skip=skip, limit=limit)

# update post by post id


@router.put("/Updatepost/{post_id}", response_model=schemas.PostRead)
async def update_post_route(
        post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Update post by post id """
    updated_post = post_crud.update_post(db=db, post_id=post_id, post=post)
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return updated_post


@router.delete("/Deletepost/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_route(
        post_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Delete post by post id """
    if not post_crud.delete_post(db=db, post_id=post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="post not found or has been deleted")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Post deleted successfully"})


@router.get("/GetRecentPostDuration/{user_id}")
async def get_recent_post_duration(
        user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the duration of posts in the last 5 days for a user

    Notes: the challenge id is added for testing otherwise is hard to locate the specific post
    """
    return post_crud.get_recent_post_duration(db, user_id)


@router.get("/GetRecommendedPosts/{user_id}")
async def get_recommended_posts(
        user_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the recommended posts for a user

    raise HTTPException: user not found
    """
    read_user_by_id(db, user_id)  # handle user not found
    recommended_post_ids = get_recommended_post(user_id)
    blocked_user_list = block_crud.get_blocked_user_list(
        db=db, blocker_user_id=user_id)
    final_post_ids = []
    for post_id in recommended_post_ids:
        if post_id not in blocked_user_list:
            final_post_ids.append(post_id)
    return post_crud.get_posts_by_ids(db, final_post_ids)


def create_empty_csv():
    """ 
        Create an empty csv file with headers
    """
    with open(REPORT_FILE_PATH, "w", encoding="utf-8") as file:
        file.write("ID, time, user_id, post_id, report_reason\n")


def add_record_to_csv(input_data: dict):
    """ Add a record at the end of csv file

    input_data: a dictionary with keys: user_id, post_id, report_reason
    """
    # Read the file to count the number of lines
    with open(REPORT_FILE_PATH, "r", encoding="utf-8") as file:
        number_of_lines = len(file.read().strip().split("\n"))

    # Generate the new record ID and the current time
    record_id = number_of_lines
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create the new record
    record = f"{record_id}, {current_time}, {input_data['user_id']}, {input_data['post_id']}, {input_data['report_reason']}"

    # Append the new record to the file
    with open(REPORT_FILE_PATH, "a", encoding="utf-8") as file:
        file.write(record + "\n")


@router.post("/reportPost/")
async def create_report_post(
        post_id: int, user_id: int, report_reason: str, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the report post for a user

    raise HTTPException: user not found
    """
    read_user_by_id(db, user_id)  # handle user not found
    new_data = {}
    if not os.path.exists(REPORT_FILE_PATH):
        create_empty_csv()
        new_data = {
            "user_id": user_id,
            "post_id": post_id,
            "report_reason": report_reason
        }
        add_record_to_csv(new_data)
    else:
        new_data = {
            "user_id": user_id,
            "post_id": post_id,
            "report_reason": report_reason
        }
        add_record_to_csv(new_data)

    return new_data
