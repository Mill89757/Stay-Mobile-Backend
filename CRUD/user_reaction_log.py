from sqlite3 import dbapi2
from sqlalchemy.orm import Session
import models, schemas
from fastapi import HTTPException, status
from typing import List

# create user reaction log
def create_user_reaction_log(db:Session, log:schemas.UserReactionLogCreate):
    db_log = models.User_reaction_log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# read all user reaction log
def get_user_reaction_log(db:Session, skip:int=0, limit:int=100):
    log_list = db.query(models.User_reaction_log).offset(skip).limit(limit).all()
    if log_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return log_list

# read user reaction log by log id
def get_user_reaction_log_by_log_id(db:Session, log_id:int):
    user_reaction_log = db.query(models.User_reaction_log).filter(models.User_reaction_log.log_id == log_id).all()
    if user_reaction_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return user_reaction_log

# read user reaction log by user id
def get_user_reaction_log_by_user_id(db:Session, user_id:int) -> List[models.User_reaction_log]:
    user_reaction_logs = db.query(models.User_reaction_log).filter(models.User_reaction_log.user_id == user_id).all()
    if user_reaction_logs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return user_reaction_logs

# read user reaction log by post id
def get_user_reaction_log_by_post_id(db:Session, post_id:int) -> List[models.User_reaction_log]:
    user_reaction_logs = db.query(models.User_reaction_log).filter(models.User_reaction_log.post_id == post_id).all()
    if user_reaction_logs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return user_reaction_logs

# read user reaction log by emoji id
def get_user_reaction_log_by_emoji(db:Session, emoji_image:str) -> List[models.User_reaction_log]:
    user_reaction_logs = db.query(models.User_reaction_log).filter(models.User_reaction_log.emoji_image == emoji_image).all()
    if user_reaction_logs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return user_reaction_logs

# update user reaction log by log id
def update_user_reaction_log(db:Session, log_id:int, log:schemas.UserReactionLogCreate):
    db_log = db.query(models.User_reaction_log).filter(models.User_reaction_log.log_id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    for key, value in log.dict(exclude_unset=True).items():
        setattr(db_log, key, value)
    db.commit
    return db_log

# delete user reaction log by log id
def delete_user_reaction_log(db:Session, log_id:int):
    db_log = db.query(models.User_reaction_log).filter(models.User_reaction_log.log_id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    db.delete(db_log)
    db.commit()

# read most recently user reaction log by user id, post id and datetime
def get_recent_user_reaction_log_by_user_id(db:Session, user_id:int, post_id:int):
    user_reaction_log = db.query(models.User_reaction_log).filter(models.User_reaction_log.user_id == user_id, models.User_reaction_log.post_id==post_id).order_by(models.User_reaction_log.created_datetime.desc).first()
    return user_reaction_log