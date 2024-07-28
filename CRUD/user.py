from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas


def create_user(db: Session, user: schemas.UsersRequest):
    """ Create user """
    db_user = models.User(
        firebase_uid=user.firebase_uid,
        name=user.name,
        username=user.username,
        email_address=user.email_address,
        created_time=user.created_time,
        avatar_location=user.avatar_location,
        is_completed=user.is_completed,
        user_timezone=user.user_timezone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def read_users(db: Session):
    """ Read all users """
    return db.query(models.User).all()


def read_user_by_id(db: Session, user_id: int):
    """ Read user by id """
    user = db.query(models.User)\
        .filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def read_user_by_firebase_uid(db: Session, firebase_uid: str):
    """ Read user by firebase_uid """
    user = db.query(models.User).filter(
        models.User.firebase_uid == firebase_uid).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_user(db: Session, user_id: int, user: schemas.UsersRequest):
    """ Update user """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    db.query(models.User).filter(models.User.id == id).update(
        {
            "firebase_uid": user.firebase_uid,
            "name": user.name,
            "username": user.username,
            "email_address": user.email_address,
            "created_time": user.created_time,
            "avatar_location": user.avatar_location,
            "is_completed": user.is_completed,
        }
    )
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_is_complete(db: Session, firebase_uid: str, user: schemas.UsersRequest):
    """ Update user is_completed which means user has been complete the who registration process """
    db_user = db.query(models.User).filter(
        models.User.firebase_uid == firebase_uid).first()
    if db_user is None:
        return None
    db.query(models.User).filter(models.User.firebase_uid == firebase_uid).update(
        {
            "firebase_uid": user.firebase_uid,
            "name": user.name,
            "username": user.username,
            "email_address": user.email_address,
            "created_time": user.created_time,
            "avatar_location": user.avatar_location,
            "is_completed": user.is_completed,
        }
    )
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    """ Delete user by id """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return True
