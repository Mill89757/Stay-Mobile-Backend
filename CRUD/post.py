from typing import List
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas

def create_post(db: Session, post: schemas.PostCreate):
    
    challenge = db.query(models.Challenge).filter(models.Challenge.id == post.challenge_id).first()
    current_breaking_days_left = (db.query(models.GroupChallengeMembers).filter(models.GroupChallengeMembers.challenge_id == post.challenge_id).filter(models.GroupChallengeMembers.user_id == post.user_id).first())
    if not challenge:
        return "Challenge not found"

    new_days_left = challenge.days_left - 1
    new_breaking_days_left = current_breaking_days_left.breaking_days_left - (1 if post.start_time == post.end_time else 0)

    if new_days_left < 0 or new_breaking_days_left < 0:
        return "Cannot create post as it would result in negative days left or breaking days left"

    db_post = models.Post(
        user_id=post.user_id,
        challenge_id=post.challenge_id,
        start_time=post.start_time,
        end_time=post.end_time,
        written_text=post.written_text,
    )
    db.add(db_post)
    db.commit()
    challenge.days_left = new_days_left
    current_breaking_days_left.breaking_days_left = new_breaking_days_left
    db.commit()
    db.refresh(db_post)

    db_post_content = models.PostContent(
        post_id=db_post.id,
        video_location = None,
        image_location = post.image_location,
        voice_location = None,
    )
    db.add(db_post_content)
    db.commit()
    db.refresh(db_post_content)

    return db_post

# read post by post id
def get_post(db:Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

# read all posts
def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

# read posts of one user by user id
def get_posts_by_user_id(db: Session, user_id: int) -> List[models.Post]:
    user_id_posts = (
        db.query(models.Post)
        .filter(models.Post.user_id == user_id)
        .all()
    )
    return user_id_posts

# read posts by challenge id
def get_posts_by_challenge_id(db: Session, challenge_id: int) -> List[models.Post]:
    challenge_id_posts = (
        db.query(models.Post)
        .filter(models.Post.challenge_id == challenge_id)
        .all()
    )
    return challenge_id_posts

# update post by post id
def update_post(db: Session, post_id: int, post: schemas.PostCreate):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    for key, value in post.dict(exclude_unset=True).items():
        setattr(db_post, key, value)
    db.commit()
    return db_post

# delete post by post id
def delete_post(db: Session, post_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"detail": "Post has been deleted"}