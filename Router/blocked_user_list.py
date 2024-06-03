from lib2to3.pgen2 import token
from os import stat
from webbrowser import get
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas
from database import get_db
import CRUD.blocked_user_list as crud

 # create routes for blocked user list operations and functions
router = APIRouter(prefix="/blocked_user")

# create blocked user relationship
@router.post("/create", response_model=schemas.BlockUserListBase, status_code=status.HTTP_201_CREATED)
async def create_blocked_user(blocked_user: schemas.BlockUserListBase, db:Session=Depends(get_db)):
    blocked_user= crud.create_blocked_user(db=db,blocked_user=blocked_user)
    return blocked_user

# get blocked user relationship 
@router.get("/getBlockedUser/{blocker_user_id}/{blocked_user_id}", response_model=schemas.BlockUserListBase)
async def get_blocked_user(blocker_user_id:int, blocked_user_id: int, db:Session=Depends(get_db)):
    blocked_user = crud.get_blocked_user(db=db, blocker_user_id=blocker_user_id, blocked_user_id=blocked_user_id)
    return blocked_user

# get blocked user list by blocker user id
@router.get("/getBlockedUserList/{blocker_user_id}")
async def get_blocked_user_list(blocker_user_id:int, db:Session=Depends(get_db)):
    blocker_user_list = crud.get_blocked_user_list(db=db, blocker_user_id=blocker_user_id)
    return blocker_user_list

# delete blocked user relationship by blocker user id & blocked user id
@router.delete("/deleteBlockedUser/{blocker_user_id}/{blocked_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blocked_user(blocker_user_id: int, blocked_user_id:int, db:Session=Depends(get_db)):
    if not crud.delete_blocked_user(db=db, blocker_user_id=blocker_user_id, blocked_user_id=blocked_user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail":"Blocked user has been deleted success."})

# get blocked user info list
@router.get("/getBlockedUserInfoList/{blocker_user_id}")
async def get_blocked_user_info_list(blocker_user_id: int, db:Session=Depends(get_db)):
    user_info_list = crud.get_username_avatar(db=db, blocker_user_id=blocker_user_id)
    if user_info_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user_info_list