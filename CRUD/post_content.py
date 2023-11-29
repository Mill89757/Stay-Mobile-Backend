from typing import List
from sqlalchemy.orm import Session
import models, schemas  
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas

# crate post content
def create_post_content(db: Session, post_content: schemas.PostContentCreate):
    db_post_content = models.PostContent(**post_content.dict())
    db.add(db_post_content)
    db.commit()
    db.refresh(db_post_content)
    return db_post_content

# read post content by post content id
def get_post_content(db:Session, post_content_id: int):
    post_content = db.query(models.PostContent).filter(models.PostContent.id == post_content_id).first()
    if post_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post_content not found")
    return post_content

# read all post content
def get_post_contents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PostContent).offset(skip).limit(limit).all()

# read post content by post id
def get_post_contents_by_post_id(db: Session, post_id: int) -> List[models.PostContent]:
    post_id_post_contents = (
        db.query(models.PostContent)
        .filter(models.PostContent.post_id == post_id)
        .all()
    )
    return post_id_post_contents

# update post content by post content id
def update_post_content(db: Session, post_content_id: int, post_content: schemas.PostContentCreate):
    db_post_content = db.query(models.PostContent).filter(models.PostContent.id == post_content_id).first()
    if db_post_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post_content not found")
    for key, value in post_content.dict(exclude_unset=True).items():
        setattr(db_post_content, key, value)
    db.commit()
    return db_post_content

# delete post content by post content id
def delete_post_content(db: Session, post_content_id: int):
    db_post_content = db.query(models.PostContent).filter(models.PostContent.id == post_content_id).first()
    if db_post_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post_content not found")
    db.delete(db_post_content)
    db.commit()
    return {"detail": "post_content has been deleted"}