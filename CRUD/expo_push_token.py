from pyexpat import model
from statistics import mode
from time import timezone
from typing import List
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime as dt

def create_expo_push_token(db:Session, expo_push_token: schemas.ExpoPushTokenBase):
    """ User may delete their app and reinstall it, so we need to update the token"""
    db_token = db.query(models.ExpoPushToken).filter(models.ExpoPushToken.expo_push_token == expo_push_token).first()
    if db_token is None:
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
    return db_token


def get_tokens(db:Session):
    expo_tokens = db.query(models.ExpoPushToken).all()
    if expo_tokens is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expo push token not found")
    return expo_tokens

def get_expo_push_token(db:Session, user_id:int):
    expo_push_token = db.query(models.ExpoPushToken).filter(models.ExpoPushToken.user_id == user_id).first()
    if expo_push_token is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expo push token not found")
    return expo_push_token

def update_expo_push_token(db:Session, token: str, tokenInfo: schemas.ExpoPushTokenBase):
    db_token = db.query(models.ExpoPushToken).filter(models.ExpoPushToken.expo_push_token == token).first()
    if db_token.timestamp < tokenInfo.timestamp:
        for key, value in tokenInfo.dict(exclude_unset=True).items():
            setattr(db_token, key, value)
    db.commit()
    return db_token

def delete_token_uid(db:Session, uid:int):
    db_token = db.query(models.ExpoPushToken).filter(models.ExpoPushToken.user_id == uid).first()
    if db_token is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expo push token not found")
    db.delete(db_token)
    db.commit()
    return{"detail": "Expo Push Token has been deleted"}

def delete_token_by_token(db:Session, token:str):
    db_token = db.query(models.ExpoPushToken).filter(models.ExpoPushToken.expo_push_token==token).first()
    if db_token is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expo push token not found")
    db.delete(db_token)
    db.commit()
    return{"detail": "Expo Push Token has been deleted"}

