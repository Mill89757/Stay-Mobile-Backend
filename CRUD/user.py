from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
import re
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


# convert string to datetime (keep it here for now)
# def convert_datetime(string):
#     split_list = re.split("-|:| ", string)
#     temp_list = []
#     for i in split_list:
#         temp_list.append(int(i))
#     result = datetime(
#         temp_list[0],
#         temp_list[1],
#         temp_list[2],
#         temp_list[3],
#         temp_list[4],
#         temp_list[5],
#     )
#     return result

#create user
def create_user(db: Session, user: schemas.UsersRequest):
    db_user = models.User(
        firebase_uid=user.firebase_uid,
        name=user.name,
        username=user.username,
        email_address=user.email_address,
        # created_time=convert_datetime(user.created_time),
        created_time = user.created_time,
        avatar_location=user.avatar_location,
        is_completed=user.is_completed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#read all users
def read_users(db: Session):
    return db.query(models.User).all()

#read user by id
def read_user_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()

#read user by firebase_uid
def read_user_by_firebase_uid(db: Session, firebase_uid: str):
    return db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()

#update user
def update_user(db: Session, id: int, user: schemas.UsersRequest):
    db_user = db.query(models.User).filter(models.User.id == id).first()
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

#update user is_completed to true when user complete the profile by firebase_uid
def update_user_is_complete(db: Session, firebase_uid: str, user: schemas.UsersRequest):
    db_user = db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()
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

#delete user
def delete_user(db: Session, id: int):
    db_user = db.query(models.User).filter(models.User.id == id).first()
    if db_user is None:
        return None
    db.query(models.User).filter(models.User.id == id).delete()
    db.commit()
    return True