from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models
import schemas


def create_emoji(db: Session, emoji: schemas.EmojiBase):
    """ Create new emoji """
    db_emoji = models.Emoji(**emoji.dict())
    db.add(db_emoji)
    db.commit()
    db.refresh(db_emoji)
    return db_emoji


def get_emoji(db: Session, emoji_str: str):
    """ Get emoji by emoji description """
    emoji = db.query(models.Emoji).filter(
        models.Emoji.emoji_image == emoji_str).first()
    if emoji is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Emoji not found")
    return emoji


def get_emojis(db: Session, skip: int = 0, limit: int = 100):
    """ Get all emojis """
    return db.query(models.Emoji).offset(skip).limit(limit).all()


def get_emojis_by_name(db: Session, name: str) -> List[models.Emoji]:
    """ Get emojis by name """
    name_emojis = (
        db.query(models.Emoji)
        .filter(models.Emoji.name == name)
        .all()
    )
    return name_emojis


def update_emoji(db: Session, emoji_image: str, emoji: schemas.EmojiBase):
    """ Update emoji """
    db_emoji = db.query(models.Emoji).filter(
        models.Emoji.emoji_image == emoji_image).first()
    if db_emoji is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Emoji not found")
    for key, value in emoji.dict(exclude_unset=True).items():
        setattr(db_emoji, key, value)
    db.commit()
    return db_emoji


def delete_emoji(db: Session, emoji_image: str):
    """ Delete emoji """
    db_emoji = db.query(models.Emoji).filter(
        models.Emoji.emoji_image == emoji_image).first()
    if db_emoji is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Emoji not found")
    db.delete(db_emoji)
    db.commit()
    return {"detail": "Emoji has been deleted"}
