from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import CRUD.post as post_crud
import CRUD.user as user_crud
import models
import schemas


def create_user_reaction_log(db: Session, log: schemas.UserReactionLogCreate):
    """ Create user reaction log

    Args:
    db (Session): database session
    log (schemas.UserReactionLogCreate): user reaction log data

    Returns:

    models.UserReactionLog: created user reaction log

    Raises:
    HTTPException: if user does not exist
    HTTPException: if post does not exist
    HTTPException: if emoji is invalid
    """
    user_crud.read_user_by_id(db, log.user_id)      # check if user exists
    post_crud.get_post(db, log.post_id)             # check if post exists
    if log.emoji_image.isascii():                   # check if emoji is valid
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Emoji image must be an emoji")
    existing_log = get_recent_user_reaction_log_by_user_id(
        db=db, user_id=log.user_id, post_id=log.post_id)
    if existing_log and not existing_log.is_cancelled and\
            existing_log.emoji_image != log.emoji_image:
        return "User can only create one reaction in one post"
    db_log = models.UserReactionLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_user_reaction_log(db: Session, skip: int = 0, limit: int = 100):
    """ Get all user reaction log """
    log_list = db.query(models.UserReactionLog).offset(skip).limit(limit).all()
    if log_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user reaction log found")
    return log_list


def get_user_reaction_log_by_log_id(db: Session, log_id: int) -> List[models.UserReactionLog]:
    """ Get user reaction log by log id """
    user_reaction_log = db.query(models.UserReactionLog).filter(
        models.UserReactionLog.log_id == log_id).all()
    if user_reaction_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user reaction log found")
    return user_reaction_log


def get_user_reaction_log_by_user_id(db: Session, user_id: int) -> List[models.UserReactionLog]:
    """ Get user reaction log by user id """
    user_reaction_logs = db.query(models.UserReactionLog).filter(
        models.UserReactionLog.user_id == user_id).all()
    if not user_reaction_logs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user reaction log found")
    return user_reaction_logs


def get_user_reaction_log_by_post_id(db: Session, post_id: int) -> List[models.UserReactionLog]:
    """ Get user reaction log by post id """
    user_reaction_logs = db.query(models.UserReactionLog).filter(
        models.UserReactionLog.post_id == post_id).all()
    if user_reaction_logs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user reaction log found")
    return user_reaction_logs


def get_user_reaction_log_by_emoji(db: Session, emoji_image: str) -> List[models.UserReactionLog]:
    """ Get user reaction log by emoji image """
    user_reaction_logs = db.query(models.UserReactionLog).filter(
        models.UserReactionLog.emoji_image == emoji_image).all()
    if user_reaction_logs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user reaction log found")
    return user_reaction_logs


def update_user_reaction_log(db: Session, log_id: int, log: schemas.UserReactionLogCreate):
    """ Update user reaction log """
    user_crud.read_user_by_id(db, log.user_id)          # check if user exists
    post_crud.get_post(db, log.post_id)                 # check if post exists
    if log.emoji_image.isascii():                       # check if emoji is valid
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Emoji image must be an emoji")
    db_log = db.query(models.UserReactionLog).filter(
        models.UserReactionLog.log_id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user reaction log found")
    for key, value in log.dict(exclude_unset=True).items():
        setattr(db_log, key, value)
    db.commit()
    return db_log


def delete_user_reaction_log(db: Session, log_id: int):
    """ Delete user reaction log by log id """
    db_log = db.query(models.UserReactionLog).filter(
        models.UserReactionLog.log_id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user reaction log found")
    db.delete(db_log)
    db.commit()


def get_recent_user_reaction_log_by_user_id(db: Session, user_id: int, post_id: int):
    """ Get most recent user reaction log by user id, post id and datetime """
    user_reaction_log = db.query(models.UserReactionLog)\
        .filter(models.UserReactionLog.user_id == user_id,
                models.UserReactionLog.post_id == post_id)\
        .order_by(models.UserReactionLog.created_datetime.desc()).first()
    return user_reaction_log
