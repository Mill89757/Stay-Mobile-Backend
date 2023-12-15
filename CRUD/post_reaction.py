from typing import List
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas


def creat_post_reaction(db: Session, post_reaction: schemas.PostReactionCreate):
    db_post_reaction = models.PostReaction(**post_reaction.dict())
    db.add(db_post_reaction)
    db.commit()
    db.refresh(db_post_reaction)
    return db_post_reaction

def get_post_reactions_by_postid(db:Session, post_id: int):
    postid_post_reactions = db.query(models.PostReaction).filter(models.PostReaction.post_id == post_id).first()
    if postid_post_reactions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Reaction not found")
    return postid_post_reactions

def get_post_reactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PostReaction).offset(skip).limit(limit).all()

def get_post_reactions_by_emoji_image(db: Session, emoji_image: str) -> List[models.PostReaction]:
    emoji_image_post_reactions = (
        db.query(models.PostReaction)
        .filter(models.PostReaction.emoji_image == emoji_image)
        .all()
    )
    return emoji_image_post_reactions

def get_post_reactions_by_count(db: Session, count: int) -> List[models.PostReaction]:
    count_post_reactions = (
        db.query(models.PostReaction)
        .filter(models.PostReaction.count == count)
        .all()
    )
    return count_post_reactions

def update_post_reaction(db: Session, post_id: int, emoji_image: str, post_reaction: schemas.PostReactionCreate):
    db_post_reaction = db.query(models.PostReaction).filter(models.PostReaction.post_id == post_id, models.PostReaction.emoji_image == emoji_image).first()
    if db_post_reaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Reaction not found")
    for key, value in post_reaction.dict(exclude_unset=True).items():
        setattr(db_post_reaction, key, value)
    db.commit()
    return db_post_reaction

def delete_post_reaction(db: Session, post_id: int, emoji_image: str):
    db_post_reaction = db.query(models.PostReaction).filter(models.PostReaction.post_id == post_id, models.PostReaction.emoji_image == emoji_image).first()
    if db_post_reaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Reaction not found")
    db.delete(db_post_reaction)
    db.commit()
    return {"detail": "Post Reaction has been deleted"}