import models
import schemas
from sqlalchemy.orm import Session
import re
from datetime import datetime

def convert_datetime(string):
    split_list = re.split("-|:| ", string)
    temp_list = []
    for i in split_list:
        temp_list.append(int(i))
    result = datetime(
        temp_list[0],
        temp_list[1],
        temp_list[2],
        temp_list[3],
        temp_list[4],
        temp_list[5],
    )
    return result

def create_user(db: Session, user: schemas.UsersRequest):
    db_user = models.User(
        firebase_uid=user.firebase_uid,
        name=user.name,
        username=user.username,
        email_address=user.email_address,
        created_time=convert_datetime(user.created_time),
        avatar_location=user.avatar_location,
        iscompleted = user.iscompleted,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def read_user(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()

def read_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email_address == email).first()

def read_users(db: Session):
    return db.query(models.User).all()

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
            "created_time": convert_datetime(user.created_time),
            "avatar_location_location": user.avatar_location,
            "iscompleted": user.iscompleted,
        }
    )
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, id: int):
    db_user = db.query(models.User).filter(models.User.id == id).first()
    if db_user is None:
        return None
    db.query(models.User).filter(models.User.id == id).delete()
    db.commit()
    return True