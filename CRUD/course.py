from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models

# Read all courses
def read_course(db: Session):
    return db.query(models.Course).all()

# Read course by id
def read_course_by_id(db: Session, id: int):
    db_course = db.query(models.Course).filter(models.Course.id == id).first()
    if db_course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return db_course