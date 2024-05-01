from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas  
from database import get_db  
import CRUD.post as post_crud
import random
from r1_automation import byte_to_utf8
from redis_client import redis_client
from CRUD.user import read_user_by_id
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials, auth, initialize_app
from auth_dependencies import verify_token, conditional_depends
from datetime import datetime
import os


# create routes for posts operations and functions
router = APIRouter()

# # 设置OAuth2的Bearer类型认证模式
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # 依赖项: 解析并验证JWT
# def verify_token(token: str = Depends(oauth2_scheme)):
#     try:
#         print(token)
#         # 验证JWT
#         payload = auth.verify_id_token(token)
#         print(payload)
#         return payload
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail='Could not validate credentials',
#             headers={"WWW-Authenticate": "Bearer"},
#         )

# create post 
@router.post("/CreatePost/", response_model=schemas.PostRead, status_code=status.HTTP_201_CREATED)
async def create_post_router(post:schemas.PostCreate, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):

    result = post_crud.create_post(db=db, post = post)
    if isinstance(result, str) and "Cannot create post" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
    
    print(current_user)
    return result

# read post by post id
@router.get("/GetPost/{post_id}", response_model=schemas.PostRead)
async def get_post_route(post_id: int, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the post by post id
    
    Args:
        post_id (int): post id
    
    Returns:
        post: post object    

    Raises:
        HTTPException: post not found
    """
    post = post_crud.get_post(db=db, post_id=post_id)
    print(current_user)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post

# read posts of one user by user id
@router.get("/GetPostByUserID/{user_id}", response_model=List[schemas.PostRead])
async def get_post_route_user_id(user_id: int, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the post by user id
    
    Args:
        user_id (int): user id
    
    Returns:
        post: post object
        
    Raises:
        HTTPException: post not found
        HTTPException: user not found
    """
    post = post_crud.get_posts_by_user_id(db=db, user_id = user_id)
    print(current_user)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post

# read posts by challenge id
@router.get("/GetPostByChallengeID/{challenge_id}", response_model=List[schemas.PostRead])
async def get_post_route_challenge_id(challenge_id: int, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the post by challenge id

    Args:
        challenge_id (int): challenge id

    Returns:
        post: post object
    
    Raises:
        HTTPException: post not found
        HTTPException: challenge not found
    """
    post = post_crud.get_posts_by_challenge_id(db=db, challenge_id = challenge_id)
    print(current_user)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post

# read all posts
@router.get("/GetAllposts/", response_model=list[schemas.PostRead])
async def get_posts_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """ Return all posts
    
    Args:
        skip (int): skip
        limit (int): limit
    
    Returns:
        list of posts object
    """
    print(current_user)
    return post_crud.get_posts(db=db, skip=skip, limit=limit)

# update post by post id
@router.put("/Updatepost/{post_id}", response_model=schemas.PostRead)
async def update_post_route(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    updated_post = post_crud.update_post(db=db, post_id=post_id, post=post)
    print(current_user)
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return updated_post

# delete post by post id
@router.delete("/Deletepost/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_route(post_id: int, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    print(current_user)
    if not post_crud.delete_post(db=db, post_id=post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found or has been deleted")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Post deleted successfully"})

# read the recent post duration for a user
@router.get("/GetRecentPostDuration/{user_id}")
async def get_recent_post_duration(user_id: int, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the duration of posts in the last 5 days for a user
    
    Notes: the challenge id is added for testing otherwise is hard to locate the specific post
    """
    print(current_user)
    return post_crud.get_recent_post_duration(db, user_id)

def top3categories(user_id:int) -> set:
    """
    the 'user_contribution' key in redis is a hash table that record user's contribution to each challenge category.
    this function takes user_id as input and return 3 categories where the user has spent the most time contributing.
    """
    
    # retrive uer's challenge contribution data.
    contribution = byte_to_utf8( redis_client.hget('user_contribution',user_id), StrToSplit=',', ifError=['0']*5)
    contribution = [int(num) for num in contribution]

    topCategories = []

    for category in range(5):

        # if user did not contribute to category i, then move on to the next category
        if contribution[category] == 0: continue 

        # otherwise, see if user's contribution is one of the top 3 cateogries. 
        for i in range(len(topCategories)):
            if contribution[category] > contribution[topCategories[i]]: 
                topCategories.insert(i, category)
                continue
        if len(topCategories) < 3: 
            contribution.append(category)
        elif len(topCategories) > 3:
            contribution.pop()

    # if user contributed to less than 3 categories, 
    # then randomly pick some other categories for this user
    n = len(topCategories)
    if n == 3:
        return topCategories
    other_categories = [item for item in [0,1,2,3,4] if item not in topCategories]
    return  topCategories + random.sample(other_categories, 3-n)


def filteredPosts_from_reacted_challenges(user_id:int) -> list:
    """
    user can interact with posts, each post belongs to 1 challenge.
    so reacting to recent post is equivalent to react to a challenge.
    this function allocates new posts to users based on their interacted challenges.
    """
    postPool = []
    recent_posts = redis_client.hkeys('post_clg_pair')
    recent_posts = random.sample(recent_posts, min(len(recent_posts),200))
    top3 = top3categories(user_id)

    for post_id in recent_posts:
        clg_id = redis_client.hget('post_clg_pair', post_id)
        category = int(byte_to_utf8(redis_client.hget('on_clg_info', clg_id), StrToSplit=',')[0])
        if category not in top3:
            interacted_post = redis_client.sismember(f'{user_id}_liked_posts', post_id)
            interacted_clg = redis_client.zscore(f'{user_id}_clgs_preference',post_id)
            if not interacted_post or interacted_clg:
                postPool.append(int(byte_to_utf8(post_id)))
    
    return postPool


def filteredPosts_from_top3Categories(user_id:int) -> list:
    top3 = top3categories(user_id)
    postPool = []

    for category_code in top3:

        # get all recent post from specified category
        raw_post_pool = redis_client.zrangebyscore(f'recent_posts_for_category{category_code}', 0, float('inf'))
        raw_post_pool = [int(post) for post in raw_post_pool]
        raw_post_pool = random.sample(raw_post_pool, min(len(raw_post_pool), 100))
        
        for post_id in raw_post_pool: 
            if not redis_client.sismember(f'{user_id}_liked_posts', post_id): postPool.append(post_id)
    
    return postPool


def get_recommended_post(user_id):
    return filteredPosts_from_reacted_challenges(user_id) + filteredPosts_from_top3Categories(user_id)

@router.get("/GetRecommendedPosts/{user_id}")
async def get_recommended_posts(user_id: int, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the recommended posts for a user

    raise HTTPException: user not found
    """
    # print(current_user)
    read_user_by_id(db, user_id)#handle user not found
    recommended_post_ids = get_recommended_post(user_id)
    return post_crud.get_posts_by_ids(db, recommended_post_ids)

REPORT_FILE_PATH = "report_content.csv"

def create_empty_csv():
    """ Create an empty csv file with headers
    """
    with open(REPORT_FILE_PATH, "w") as file:
        file.write("ID, time, user_id, post_id, report_reason\n")


def add_record_to_csv(input_data: dict):
    """ Add a record at the end of csv file

    input_data: a dictionary with keys: user_id, post_id, report_reason
    """
    file = open(REPORT_FILE_PATH, "r")
    number_of_lines = len(file.read().split("\n"))
    id = number_of_lines - 1
    file.close()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = f"{id}, {time}, {input_data['user_id']}, {input_data['post_id']}, {input_data['report_reason']}"
    with open(REPORT_FILE_PATH, "a") as file:
        file.write(record + "\n") 

@router.post("/reportPost/")
async def create_report_post(post_id:int ,user_id: int, report_reason:str, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """ Return the report post for a user

    raise HTTPException: user not found
    """
    read_user_by_id(db, user_id)#handle user not found
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