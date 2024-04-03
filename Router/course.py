from re import S
from typing import List
from webbrowser import get
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from models import Challenge
import schemas
from database import SessionLocal
import CRUD.course as crud
import CRUD.challenge 
from database import get_db
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials, auth, initialize_app
from firebase_setup import firebase_app
from auth_dependencies import verify_token, conditional_depends

# create route for courses operation and functions
router = APIRouter(prefix="/courses")

# # 设置OAuth2的Bearer类型认证模式
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # 依赖项: 解析并验证JWT
# def verify_token(token: str = Depends(oauth2_scheme)):
#     try:
#         print(token)
#         # 验证JWT
#         payload = auth.verify_id_token(token)
#         print(payload)
#         return payload
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail='Could not validate credentials',
#             headers={"WWW-Authenticate": "Bearer"},
#         )

# read all courses
@router.get("", response_model=List[schemas.CourseResponse])
async def get_course_data(db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """Read all courses from database
    
    Returns:
        List[Course]: list of courses
    """
    course_data = crud.read_course(db)
    print(current_user)
    return course_data

# read course by course id
@router.get("/{id}", response_model=schemas.CourseResponse)
async def get_course_by_id(id: int, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """Read course by id

    Args:
        id (int): course id
    
    Returns:
        Course: course data
    
    Raises:
        HTTPException: course not found
    """
    print(current_user)
    course = crud.read_course_by_id(db, id)
    if course is None:
        raise HTTPException(status_code=404, detail="course not found")
    return course

# update course and challenge relationship
@router.put("/LinkCourseChallenge/{course_id}/{challenge_id}", response_model=schemas.ChallengeRead)
async def update_challenge_course_id(course_id:int, challenge_id:int, db: Session=Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """update challenge course_id by challenge id and course id
    
    Args:
        challenge_id: id of challenge
        course_id: id of course

    Raises:
        HTTPException: challenge not found
        HTTPException: challenge has been already linked to course
    """
    print(current_user)
    update_challenge =  CRUD.challenge.update_challenge_course_id(db, challenge_id, course_id)
    return update_challenge
