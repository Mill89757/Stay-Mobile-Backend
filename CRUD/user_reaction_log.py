from sqlite3 import dbapi2
from sqlalchemy.orm import Session
import models, schemas
from fastapi import HTTPException, status
from typing import List

# create user reaction log
def create_user_reaction_log(db:Session, log:schemas.UserReactionLogCreate):
    existing_log = get_recent_user_reaction_log_by_user_id(db=db,user_id=log.user_id, post_id=log.post_id)
    if existing_log is not None and existing_log.is_cancelled == False and existing_log.emoji_image != log.emoji_image:
        return "User can only create one reaction in one post"
    db_log = models.UserReactionLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# read all user reaction log
def get_user_reaction_log(db:Session, skip:int=0, limit:int=100):
    log_list = db.query(models.UserReactionLog).offset(skip).limit(limit).all()
    if log_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return log_list

# read user reaction log by log id
def get_user_reaction_log_by_log_id(db:Session, log_id:int):
    user_reaction_log = db.query(models.UserReactionLog).filter(models.UserReactionLog.log_id == log_id).all()
    if user_reaction_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return user_reaction_log

# read user reaction log by user id
def get_user_reaction_log_by_user_id(db:Session, user_id:int) -> List[models.UserReactionLog]:
    user_reaction_logs = db.query(models.UserReactionLog).filter(models.UserReactionLog.user_id == user_id).all()
    if user_reaction_logs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return user_reaction_logs

# read user reaction log by post id
def get_user_reaction_log_by_post_id(db:Session, post_id:int) -> List[models.UserReactionLog]:
    user_reaction_logs = db.query(models.UserReactionLog).filter(models.UserReactionLog.post_id == post_id).all()
    if user_reaction_logs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return user_reaction_logs

# read user reaction log by emoji id
def get_user_reaction_log_by_emoji(db:Session, emoji_image:str) -> List[models.UserReactionLog]:
    user_reaction_logs = db.query(models.UserReactionLog).filter(models.UserReactionLog.emoji_image == emoji_image).all()
    if user_reaction_logs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    return user_reaction_logs

# update user reaction log by log id
def update_user_reaction_log(db:Session, log_id:int, log:schemas.UserReactionLogCreate):
    db_log = db.query(models.UserReactionLog).filter(models.UserReactionLog.log_id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    for key, value in log.dict(exclude_unset=True).items():
        setattr(db_log, key, value)
    db.commit
    return db_log

# delete user reaction log by log id
def delete_user_reaction_log(db:Session, log_id:int):
    db_log = db.query(models.UserReactionLog).filter(models.UserReactionLog.log_id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user reaction log found")
    db.delete(db_log)
    db.commit()

# read most recently user reaction log by user id, post id and datetime
def get_recent_user_reaction_log_by_user_id(db:Session, user_id:int, post_id:int):
    user_reaction_log = db.query(models.UserReactionLog).filter(models.UserReactionLog.user_id == user_id, models.UserReactionLog.post_id==post_id).order_by(models.UserReactionLog.created_datetime.desc()).first()
    return user_reaction_log