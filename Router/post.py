from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas  
from database import get_db  
import CRUD.post as post_crud

router = APIRouter()

@router.post("/CreatePost/", response_model=schemas.PostRead, status_code=status.HTTP_201_CREATED)
async def creat_post_router(post:schemas.PostCreate, db: Session = Depends(get_db)):

    result = post_crud.creat_post(db=db, post = post)
    if isinstance(result, str) and "Cannot create post" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)

    return result

@router.get("/GetPost/{post_id}", response_model=schemas.PostRead)
async def get_post_route(post_id: int, db: Session = Depends(get_db)):
    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post

@router.get("/GetPostByUserID/{user_id}", response_model=List[schemas.PostRead])
async def get_post_route_user_id(user_id: int, db: Session = Depends(get_db)):
    post = post_crud.get_posts_by_user_id(db=db, user_id = user_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post

@router.get("/GetPostByChallengeID/{challenge_id}", response_model=List[schemas.PostRead])
async def get_post_route_challnege_id(challenge_id: int, db: Session = Depends(get_db)):
    post = post_crud.get_posts_by_challenge_id(db=db, challenge_id = challenge_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post

@router.get("/GetPost/{post_id}", response_model=schemas.PostRead)
async def get_post_route(post_id: int, db: Session = Depends(get_db)):
    post = post_crud.get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return post


@router.get("/GetAllposts/", response_model=list[schemas.PostRead])
async def get_posts_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return post_crud.get_posts(db=db, skip=skip, limit=limit)

@router.put("/Updatepost/{post_id}", response_model=schemas.PostRead)
async def update_post_route(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    updated_post = post_crud.update_post(db=db, post_id=post_id, post=post)
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return updated_post

@router.delete("/Deletepost/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_route(post_id: int, db: Session = Depends(get_db)):
    if not post_crud.delete_post(db=db, post_id=post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found or has been deleted")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Post deleted successfully"})