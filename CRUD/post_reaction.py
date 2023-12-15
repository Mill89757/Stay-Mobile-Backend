from pyexpat import model
from typing import List
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas

# create post reaction
def creat_post_reaction(db: Session, post_reaction: schemas.PostReactionCreate):
    db_post_reaction = models.PostReaction(**post_reaction.dict())
    db.add(db_post_reaction)
    db.commit()
    db.refresh(db_post_reaction)
    return db_post_reaction

# read post reaction by post id
def get_post_reactions_by_postid(db:Session, post_id: int) -> List[models.PostReaction]:
    postid_post_reactions = db.query(models.PostReaction).filter(models.PostReaction.post_id == post_id).all()
    if postid_post_reactions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Reaction not found")
    return postid_post_reactions

# read all post reaction
def get_post_reactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PostReaction).offset(skip).limit(limit).all()

# read post reaction by post id and emoji image
def get_post_reaction_by_post_emoji(db:Session, post_id:int, emoji_image:str):
    reaction_post_emoji=(
        db.query(models.PostReaction)
        .filter(models.PostReaction.post_id == post_id, 
        models.PostReaction.emoji_image== emoji_image).first()
    )

# read post reaction by emoji image
def get_post_reactions_by_emoji_image(db: Session, emoji_image: str) -> List[models.PostReaction]:
    emoji_image_post_reactions = (
        db.query(models.PostReaction)
        .filter(models.PostReaction.emoji_image == emoji_image)
        .all()
    )
    return emoji_image_post_reactions

# count is not key ???
def get_post_reactions_by_count(db: Session, count: int) -> List[models.PostReaction]:
    count_post_reactions = (
        db.query(models.PostReaction)
        .filter(models.PostReaction.count == count)
        .all()
    )
    return count_post_reactions

# update post reaction by post id and emoji image
def update_post_reaction(db: Session, post_id: int, emoji_image: str, post_reaction: schemas.PostReactionCreate):
    db_post_reaction = db.query(models.PostReaction).filter(models.PostReaction.post_id == post_id, models.PostReaction.emoji_image == emoji_image).first()
    if db_post_reaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Reaction not found")
    for key, value in post_reaction.dict(exclude_unset=True).items():
        setattr(db_post_reaction, key, value)
    db.commit()
    return db_post_reaction

# delete post reaction by post id and emoji image
def delete_post_reaction(db: Session, post_id: int, emoji_image: str):
    db_post_reaction = db.query(models.PostReaction).filter(models.PostReaction.post_id == post_id, models.PostReaction.emoji_image == emoji_image).first()
    if db_post_reaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Reaction not found")
    db.delete(db_post_reaction)
    db.commit()
    return {"detail": "Post Reaction has been deleted"}

# update count by post id and emoji image
def update_count(db:Session, post_id:int, emoji_image:str, action:bool):
    db_reaction = db.query(models.PostReaction).filter(models.PostReaction.post_id == post_id, models.PostReaction.emoji_image == emoji_image).first()
    if db_reaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Reaction not found")
    if action == True:
        db_reaction.count += 1
    else:
        db_reaction -= 1
    db.commit()
    return db_reaction

# read counts of all emoji images by post id
def get_counts_post(db:Session, post_id:int):
    postid_post_reactions = db.query(models.PostReaction).filter(models.PostReaction.post_id == post_id).all()
    if postid_post_reactions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Reaction not found")
    counts = 0
    for item in postid_post_reactions:
        counts += item.count
    return counts