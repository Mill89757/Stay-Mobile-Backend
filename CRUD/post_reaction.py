from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import CRUD.post as post_crud
import models
import schemas


def create_post_reaction(db: Session, post_reaction: schemas.PostReactionCreate):
    """ Create a new post reaction

    Args:
    db (Session): database session
    post_reaction (schemas.PostReactionCreate): post reaction schema

    Returns:
    models.PostReaction: post reaction model

    Raises:
    HTTPException: if post is not found
    """
    post_crud.get_post(db, post_reaction.post_id)  # check if post exists
    db_post_reaction = models.PostReaction(**post_reaction.dict())
    db.add(db_post_reaction)
    db.commit()
    db.refresh(db_post_reaction)
    return db_post_reaction


def get_post_reactions_by_post_id(db: Session, post_id: int) -> List[models.PostReaction]:
    """ Get post reaction by post id """
    post_crud.get_post(db, post_id)  # check if post exists
    post_id_post_reactions = db.query(models.PostReaction).filter(
        # return empty list if not found
        models.PostReaction.post_id == post_id).all()
    if post_id_post_reactions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post Reaction not found")
    return post_id_post_reactions


def get_post_reactions(db: Session, skip: int = 0, limit: int = 100):
    """ Get all post reactions """
    return db.query(models.PostReaction).offset(skip).limit(limit).all()


def get_post_reaction_by_post_emoji(db: Session, post_id: int, emoji_image: str):
    """ Get post reaction by post id and emoji image """
    post_crud.get_post(db, post_id)  # check if post exists
    if emoji_image.isascii():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Emoji image must be an emoji")
    if db.query(models.PostReaction)\
            .filter(models.PostReaction.emoji_image == emoji_image).all() == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post Reaction not found")
    reaction_post_emoji = (
        db.query(models.PostReaction)
        .filter(models.PostReaction.post_id == post_id,
                models.PostReaction.emoji_image == emoji_image).first()
    )
    return reaction_post_emoji


def get_post_reactions_by_emoji_image(db: Session, emoji_image: str) -> List[models.PostReaction]:
    """ Get post reaction by emoji image """
    if emoji_image.isascii():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Emoji image must be an emoji")
    emoji_image_post_reactions = (
        db.query(models.PostReaction)
        .filter(models.PostReaction.emoji_image == emoji_image)
        .all()
    )
    if emoji_image_post_reactions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post reaction not found")
    return emoji_image_post_reactions


def get_post_reactions_by_count(db: Session, count: int) -> List[models.PostReaction]:
    """ Get post reaction by count """
    count_post_reactions = (
        db.query(models.PostReaction)
        .filter(models.PostReaction.count == count)
        .all()
    )
    return count_post_reactions


def update_post_reaction(
        db: Session, post_id: int, emoji_image: str, post_reaction: schemas.PostReactionCreate):
    """ Update post reaction by post id and emoji image """
    db_post_reaction = db.query(models.PostReaction).filter(
        models.PostReaction.post_id == post_id,
        models.PostReaction.emoji_image == emoji_image).first()
    if db_post_reaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post Reaction not found")
    for key, value in post_reaction.dict(exclude_unset=True).items():
        setattr(db_post_reaction, key, value)
    db.commit()
    return db_post_reaction


def delete_post_reaction(db: Session, post_id: int, emoji_image: str):
    """ Delete post reaction by post id and emoji image """
    db_post_reaction = db.query(models.PostReaction).filter(
        models.PostReaction.post_id == post_id,
        models.PostReaction.emoji_image == emoji_image).first()
    if db_post_reaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post Reaction not found")
    db.delete(db_post_reaction)
    db.commit()
    return {"detail": "Post Reaction has been deleted"}


def update_count(db: Session, post_id: int, emoji_image: str, action: bool):
    """ Update count by post id and emoji image """
    db_reaction = db.query(models.PostReaction).filter(
        models.PostReaction.post_id == post_id,
        models.PostReaction.emoji_image == emoji_image).first()
    if db_reaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post Reaction not found")
    if action:
        db_reaction.count += 1
    else:
        db_reaction.count -= 1
    db.commit()
    return db_reaction


def get_counts_post(db: Session, post_id: int):
    """ Get counts of all emoji images by post id """
    post_id_post_reactions = db.query(models.PostReaction).filter(
        models.PostReaction.post_id == post_id).all()
    if post_id_post_reactions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post Reaction not found")
    counts = 0
    for item in post_id_post_reactions:
        counts += item.count
    return counts
