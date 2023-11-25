from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas  
from database import get_db  
import CRUD.post_content as post_content_crud

# create routes for post contents operations and functions
router = APIRouter()

# create post content
@router.post("/CreatePostContent/", response_model=schemas.PostContentRead, status_code=status.HTTP_201_CREATED)
async def creat_post_content_router(post_content:schemas.PostContentCreate, db: Session = Depends(get_db)):
    return post_content_crud.creat_post_content(db=db, post_content= post_content)

# read post content by post content id
@router.get("/GetPostContentByID/{post_content_id}", response_model=schemas.PostContentRead)
async def get_post_content_route(post_content_id: int, db: Session = Depends(get_db)):
    post_content = post_content_crud.get_post_content(db=db, post_content_id=post_content_id)
    if post_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post content not found")
    return post_content

# read post content by post id
@router.get("/GetPostContentByPostID/{post_id}", response_model=List[schemas.PostContentRead])
async def get_post_content_route_by_post_id(post_id: int, db: Session = Depends(get_db)):
    post_content = post_content_crud.get_post_contents_by_post_id(db=db, post_id = post_id)
    if post_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post content not found")
    return post_content

# read all post contents
@router.get("/GetAllPostContent/", response_model=list[schemas.PostContentRead])
async def get_all_post_content_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return post_content_crud.get_post_contents(db=db, skip=skip, limit=limit)

# update post content by post content id
@router.put("/UpdatePostContents/{post_content_id}", response_model=schemas.PostContentRead)
async def update_post_content_route(post_content_id: int, post_content: schemas.PostContentCreate, db: Session = Depends(get_db)):
    updated_post_content = post_content_crud.update_post_content(db=db, post_content_id = post_content_id, post_content = post_content)
    if updated_post_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return updated_post_content

# delete post content by post content id
@router.delete("/DeletePostContent/{post_content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_route(post_content_id: int, db: Session = Depends(get_db)):
    if not post_content_crud.delete_post_content(db=db, post_content_id = post_content_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post content not found or has been deleted")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Post content deleted successfully"})