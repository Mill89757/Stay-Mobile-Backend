from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
import re



def read_user(db: Session):
    return db.query(models.User).all()

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
        is_completed=user.is_completed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
