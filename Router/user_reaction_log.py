from inspect import stack
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas
from database import get_db
import CRUD.user_reaction_log as crud
from typing import List, Union
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials, auth, initialize_app
from firebase_setup import firebase_app
from auth_dependencies import verify_token, conditional_depends

# create routes for user reaction log operations and functions
router = APIRouter(prefix="/user_reaction_log")

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

# create user reaction log 
@router.post("/Create", response_model=schemas.UserReactionLogCreate, status_code=status.HTTP_201_CREATED)
async def create_user_reaction_log(log:schemas.UserReactionLogCreate, db:Session=Depends(get_db), current_user: dict = conditional_depends(depends=verify_token)):
    result = crud.create_user_reaction_log(db=db, log=log)
    print(current_user)
    if isinstance(result, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)
    return result

# read all user reaction log
@router.get("", response_model=List[schemas.UserReactionLogRead])
async def get_all_log(db:Session=Depends(get_db), current_user: dict = conditional_depends(depends=verify_token)):
    print(current_user)
    all_log_data = crud.get_user_reaction_log(db)
    return all_log_data

# read user reaction log by log id
@router.get("/GetByLogId/{log_id}", response_model=List[schemas.UserReactionLogRead])
async def get_log_by_log_id(log_id:int, db:Session=Depends(get_db), current_user: dict = conditional_depends(depends=verify_token)):
    print(current_user)
    log = crud.get_user_reaction_log_by_log_id(db=db, log_id=log_id)
    return log

# read user reaction log by user id
@router.get("/GetByUserId/{user_id}", response_model=List[schemas.UserReactionLogRead])
async def get_log_by_user_id(user_id:int, db:Session=Depends(get_db), current_user: dict = conditional_depends(depends=verify_token)):
    print(current_user)
    user_log_list = crud.get_user_reaction_log_by_user_id(db=db, user_id=user_id)
    return user_log_list

# read user reaction log by post id
@router.get("/GetByPostId/{post_id}", response_model=List[schemas.UserReactionLogRead])
async def get_log_by_post_id(post_id:int, db:Session=Depends(get_db), current_user: dict = conditional_depends(depends=verify_token)):
    post_log_list = crud.get_user_reaction_log_by_post_id(db=db, post_id=post_id)
    print(current_user)
    return post_log_list

# read user reaction log by emoji id
@router.get("/GetByEmoji/{emoji_image}", response_model=List[schemas.UserReactionLogRead])
async def get_log_by_emoji_image(emoji_image:str, db:Session=Depends(get_db), current_user: dict = conditional_depends(depends=verify_token)):
    emoji_log_list = crud.get_user_reaction_log_by_emoji(db=db, emoji_image=emoji_image)
    print(current_user)
    return emoji_log_list

# read the most recent user reaction log by user id and post id
@router.get("/GetLatestByUserPost/{post_id}/{user_id}")
async def get_latest_log_of_user(post_id:int, user_id:int, db:Session=Depends(get_db), current_user: dict = conditional_depends(depends=verify_token)):
    latest_log = crud.get_recent_user_reaction_log_by_user_id(db=db, post_id=post_id, user_id=user_id)
    print(current_user)
    return latest_log

# update reaction log by log id
@router.put("/UpdateById/{log_id}",response_model=schemas.UserReactionLogRead)
async def update_reaction_log(log_id:int, log:schemas.UserReactionLogRead, db:Session=Depends(get_db), current_user: dict = conditional_depends(depends=verify_token)):
    updated_log = crud.update_user_reaction_log(db=db, log_id=log_id,log=log)
    print(current_user)
    return updated_log

# delete reaction log by log id
@router.delete("/DeleteById/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(log_id:int,  db:Session=Depends(get_db), current_user: dict = conditional_depends(depends=verify_token)):
    print(current_user)
    if not crud.delete_user_reaction_log(db=db, log_id=log_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Log deleted successfully"})