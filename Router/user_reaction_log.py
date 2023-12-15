from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas
from database import get_db
import CRUD.user_reaction_log as crud
from typing import List

# create routes for user reaction log operations and functions
router = APIRouter(prefix="/user_eaction_log")

# create user reaction log 
@router.post("/CreateLog", response_model=schemas.UserReactionLogCreate, status_code=status.HTTP_201_CREATED)
async def create_user_reaction_log(log:schemas.UserReactionLogCreate, db:Session=Depends(get_db)):
    return crud.create_user_reaction_log(db=db, log=log)

# read all user reaction log
@router.get("", response_model=List[schemas.UserReactionLogRead])
async def get_all_log(db:Session=Depends(get_db)):
    all_log_data = crud.get_user_reaction_log(db)
    return all_log_data

# read user reaction log by log id
@router.get("/GetByLogId/{log_id}", response_model=schemas.UserReactionLogRead)
async def get_log_by_log_id(log_id:int, db:Session=Depends(get_db)):
    log = crud.get_user_reaction_log_by_log_id(db=db, log_id=log_id)
    return log

# read user reaction log by user id
@router.get("/GetByUserId/{user_id}", response_model=List[schemas.UserReactionLogRead])
async def get_log_by_user_id(user_id:int, db:Session=Depends(get_db)):
    user_log_list = crud.get_user_reaction_log_by_user_id(db=db, user_id=user_id)
    return user_log_list

# read user reaction log by post id
@router.get("/GetByPostId/{post_id}", response_model=List[schemas.UserReactionLogRead])
async def get_log_by_post_id(post_id:int, db:Session=Depends(get_db)):
    post_log_list = crud.get_user_reaction_log_by_post_id(db=db, post_id=post_id)
    return post_log_list

# read user reaction log by emoji id
@router.get("/GetByEmoji/{emoji_image}", response_model=List[schemas.UserReactionLogRead])
async def get_log_by_emoji_image(emoji_image:str, db:Session=Depends(get_db)):
    emoji_log_list = crud.get_user_reaction_log_by_emoji(db=db, emoji_image=emoji_image)
    return emoji_log_list

# read the most recent user reaction log by user id and post id
@router.get("/GetLatestByUserPost/{post_id}/{user_id}", response_model=schemas.UserReactionLogRead)
async def get_latest_log_of_user(post_id:int, user_id:int, db:Session=Depends(get_db)):
    latest_log = crud.get_recent_user_reaction_log_by_user_id(db=db, post_id=post_id, user_id=user_id)
    return latest_log

# update reaction log by log id
@router.put("/UpdateById/{log_id}", response_model=schemas.UserReactionLogRead)
async def update_reaction_log(log_id:int, log:schemas.UserReactionLogRead, db:Session=Depends(get_db)):
    updated_log = crud.update_user_reaction_log(db=db, log_id=log_id,log=log)
    return updated_log

# delete reaction log by log id
@router.delete("/DeleteById/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(log_id:int,  db:Session=Depends(get_db)):
    if not crud.delete_user_reaction_log(db=db, log_id=log_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Log deleted successfully"})