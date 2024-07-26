from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models


def read_course(db: Session):
    """ Read all courses from database

    Returns:
        List[Course]: list of courses
    """
    return db.query(models.Course).all()


def read_course_by_id(db: Session, course_id: int):
    """ Read course by id

    Args:
        id (int): course id

    Returns:
        Course: course data

    Raises:
        HTTPException: course not found
    """
    db_course = db.query(models.Course).filter(
        models.Course.id == course_id).first()
    if db_course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return db_course
