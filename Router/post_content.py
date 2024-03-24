from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas  
from database import get_db  
import CRUD.post_content as post_content_crud
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials, auth, initialize_app
from firebase_setup import firebase_app

# create routes for post contents operations and functions
router = APIRouter()

# 设置OAuth2的Bearer类型认证模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 依赖项: 解析并验证JWT
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        print(token)
        # 验证JWT
        payload = auth.verify_id_token(token)
        print(payload)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={"WWW-Authenticate": "Bearer"},
        )

# create post content
@router.post("/CreatePostContent/", response_model=schemas.PostContentRead, status_code=status.HTTP_201_CREATED)
async def create_post_content_router(post_content:schemas.PostContentCreate, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    """Create a new post content in the database.
    Args:
        post_content (schemas.PostContentCreate): post content data
    Returns:
        models.PostContent: post content data
    Raises:
        HTTPException: post not found
    """
    print(current_user)
    return post_content_crud.create_post_content(db=db, post_content= post_content)

# read post content by post content id
@router.get("/GetPostContentByID/{post_content_id}", response_model=schemas.PostContentRead)
async def get_post_content_route(post_content_id: int, db: Session = Depends(get_db),current_user: dict = Depends(verify_token)):
    post_content = post_content_crud.get_post_content(db=db, post_content_id=post_content_id)
    print(current_user)
    if post_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post content not found")
    return post_content

# read post content by post id
@router.get("/GetPostContentByPostID/{post_id}", response_model=List[schemas.PostContentRead])
async def get_post_content_route_by_post_id(post_id: int, db: Session = Depends(get_db),current_user: dict = Depends(verify_token)):
    post_content = post_content_crud.get_post_contents_by_post_id(db=db, post_id = post_id)
    print(current_user)
    if post_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post content not found")
    return post_content

# read all post contents
@router.get("/GetAllPostContent/", response_model=list[schemas.PostContentRead])
async def get_all_post_content_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    print(current_user)
    return post_content_crud.get_post_contents(db=db, skip=skip, limit=limit)

# update post content by post content id
@router.put("/UpdatePostContents/{post_content_id}", response_model=schemas.PostContentRead)
async def update_post_content_route(post_content_id: int, post_content: schemas.PostContentCreate, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    updated_post_content = post_content_crud.update_post_content(db=db, post_content_id = post_content_id, post_content = post_content)
    print(current_user)
    if updated_post_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return updated_post_content

# delete post content by post content id
@router.delete("/DeletePostContent/{post_content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_route(post_content_id: int, db: Session = Depends(get_db),current_user: dict = Depends(verify_token)):

    print(current_user)
    
    if not post_content_crud.delete_post_content(db=db, post_content_id = post_content_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post content not found or has been deleted")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Post content deleted successfully"})