from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
import schemas
from database import SessionLocal
import CRUD.course as crud
import CRUD.challenge as crudch

router = APIRouter(prefix="/course")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# read all courses
@router.get("", response_model=List[schemas.CourseResponse])
def get_course_data(db: Session = Depends(get_db)):
    course_data = crud.read_course(db)
    return course_data

# read course by id
@router.get("/{id}")
def get_course_by_id(id: int, db: Session = Depends(get_db)):
    course = crud.read_course_by_id(db, id)
    if course is None:
        raise HTTPException(status_code=404, detail="course not found")
    return course

# read course by id 
@router.get("/{id}/link_all_challenge")
def get_challenges_by_course_id(id: int, db: Session = Depends(get_db)):
    challenges = crudch.get_challenges_by_course_id(db, id)
    if challenges is None:
        raise HTTPException(status_code=404, detail="None chanllenge on this course")
    return challenges