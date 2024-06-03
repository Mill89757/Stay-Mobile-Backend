from pyexpat import model
from statistics import mode
from tkinter import N
from sqlalchemy.orm import Session
import models, schemas
from fastapi import HTTPException, status
from typing import List
import CRUD.user as crud_user

def create_blocked_user(db:Session,blocked_user: schemas.BlockUserListBase):
    db_blocked_user = models.BlockedUserList(**blocked_user.dict())
    db.add(db_blocked_user)
    db.commit()
    db.refresh(db_blocked_user)
    return db_blocked_user

# read blocked user relationship by blocker user id and blocked user id
def get_blocked_user(db:Session, blocker_user_id:int, blocked_user_id:int):
    blocked_user_relationship = db.query(models.BlockedUserList).filter((models.BlockedUserList.blocker_user_id == blocker_user_id) & (models.BlockedUserList.blocked_user_id == blocked_user_id)).first()
    if blocked_user_relationship is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocked user relationship not found")
    return blocked_user_relationship

# read blocked user id list by blocker user id
def get_blocked_user_list(db:Session, blocker_user_id:int):
    final_user_id_list = []
    blocked_user_list = db.query(models.BlockedUserList).filter(models.BlockedUserList.blocker_user_id == blocker_user_id).all()
    if blocked_user_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocked user not found")
    for user in blocked_user_list:
        final_user_id_list.append(user.blocked_user_id)
    return final_user_id_list

# delete blocked user relationship by blocker user id & blocked user id
def delete_blocked_user(db:Session, blocker_user_id:int, blocked_user_id: int):
    db_blocked_user = db.query(models.BlockedUserList).filter((models.BlockedUserList.blocker_user_id == blocker_user_id) & (models.BlockedUserList.blocked_user_id == blocked_user_id)).first()
    if db_blocked_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocked user not found")
    db.delete(db_blocked_user)
    db.commit()
    return {"detail": "Blocked user has been deleted"}

def get_username_avatar(db:Session, blocker_user_id:int):
    user_list = get_blocked_user_list(db=db, blocker_user_id=blocker_user_id)
    user_info_list = []
    for id in user_list:
        user = crud_user.read_user_by_id(db=db, id=id)
        if user:
            user_info = {
                "user_id" : user.id,
                "username" : user.username, 
                "avatar_location" : user.avatar_location,
            }
            user_info_list.append(user_info)
    return user_info_list