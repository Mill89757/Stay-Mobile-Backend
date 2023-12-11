from typing import List
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas


def creat_emoji(db: Session, emoji: schemas.PostCreate):
    db_emoji = models.Emoji(**emoji.dict())
    db.add(db_emoji)
    db.commit()
    db.refresh(db_emoji)
    return db_emoji

def get_emoji(db:Session, emoji_id: int):
    emoji = db.query(models.Emoji).filter(models.Emoji.id == emoji_id).first()
    if emoji is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emoji not found")
    return emoji

def get_emojis(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Emoji).offset(skip).limit(limit).all()

def get_s_by_content(db: Session, content: str) -> List[models.Emoji]:
    content_emojis = (
        db.query(models.Emoji)
        .filter(models.Emoji.content == content)
        .all()
    )
    return content_emojis

def update_emoji(db: Session, emoji_id: int, emoji: schemas.PostCreate):
    db_emoji = db.query(models.Emoji).filter(models.Emoji.id == emoji_id).first()
    if db_emoji is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emoji not found")
    for key, value in emoji.dict(exclude_unset=True).items():
        setattr(db_emoji, key, value)
    db.commit()
    return db_emoji

def delete_emoji(db: Session, emoji_id: int):
    db_emoji = db.query(models.Emoji).filter(models.Emoji.id == emoji_id).first()
    if db_emoji is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emoji not found")
    db.delete(db_emoji)
    db.commit()
    return {"detail": "Emoji has been deleted"}