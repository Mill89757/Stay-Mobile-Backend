from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import CRUD.user as crud_user
import models
import schemas


def create_blocked_user(
        db:Session,
        blocked_user: schemas.BlockUserListBase) -> models.BlockedUserList:
    """ Create a new blocked user relationship """
    db_blocked_user = models.BlockedUserList(**blocked_user.dict())
    db.add(db_blocked_user)
    db.commit()
    db.refresh(db_blocked_user)
    return db_blocked_user

def get_blocked_user(db:Session, blocker_user_id:int, blocked_user_id:int):
    """ Read blocked user relationship by blocker user id and blocked user id """
    blocked_user_relationship = db.query(models.BlockedUserList)\
        .filter((models.BlockedUserList.blocker_user_id == blocker_user_id) \
                & (models.BlockedUserList.blocked_user_id == blocked_user_id)).first()
    if blocked_user_relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blocked user relationship not found")
    return blocked_user_relationship


def get_blocked_user_list(db:Session, blocker_user_id:int):
    """ Read blocked user id list by blocker user id """
    final_user_id_list = []
    blocked_user_list = db.query(models.BlockedUserList)\
        .filter(models.BlockedUserList.blocker_user_id == blocker_user_id).all()
    if blocked_user_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocked user not found")
    for user in blocked_user_list:
        final_user_id_list.append(user.blocked_user_id)
    return final_user_id_list

def delete_blocked_user(db:Session, blocker_user_id:int, blocked_user_id: int):
    """ Delete blocked user relationship by blocker user id & blocked user id """
    db_blocked_user = db.query(models.BlockedUserList)\
        .filter((models.BlockedUserList.blocker_user_id == blocker_user_id) \
                & (models.BlockedUserList.blocked_user_id == blocked_user_id)).first()
    if db_blocked_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocked user not found")
    db.delete(db_blocked_user)
    db.commit()
    return {"detail": "Blocked user has been deleted"}


def get_username_avatar(db:Session, blocker_user_id:int):
    """ Get username and avatar location of blocked user """
    user_list = get_blocked_user_list(db=db, blocker_user_id=blocker_user_id)
    user_info_list = []
    for user_id in user_list:
        user = crud_user.read_user_by_id(db=db, id=user_id)
        if user:
            user_info = {
                "user_id" : user.id,
                "username" : user.username, 
                "avatar_location" : user.avatar_location,
            }
            user_info_list.append(user_info)
    return user_info_list