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
# create route for courses operation and functions
router = APIRouter(prefix="/courses")

# read all courses
@router.get("", response_model=List[schemas.CourseResponse])
async def get_course_data(db: Session = Depends(get_db)):
    course_data = crud.read_course(db)
    return course_data

# read course by course id
@router.get("/{id}", response_model=schemas.CourseResponse)
async def get_course_by_id(id: int, db: Session = Depends(get_db)):
    course = crud.read_course_by_id(db, id)
    if course is None:
        raise HTTPException(status_code=404, detail="course not found")
    return course


# update course and challenge relationship
@router.put("/LinkCourseChallenge/{course_id}/{challenge_id}", response_model=schemas.ChallengeRead)
async def update_challenge_course_id(course_id:int, challenge_id:int, db: Session=Depends(get_db)):
    update_challenge =  CRUD.challenge.update_challenge_course_id(db, challenge_id, course_id)
    return update_challenge