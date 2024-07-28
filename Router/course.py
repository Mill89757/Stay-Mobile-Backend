# pylint: disable=unused-argument

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import CRUD.challenge
import CRUD.course as crud
import schemas
from auth_dependencies import conditional_depends, verify_token
from database import get_db

router = APIRouter(prefix="/courses")


@router.get("", response_model=List[schemas.CourseResponse])
async def get_course_data(
        db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read all courses from database

    Returns:
        List[Course]: list of courses
    """
    course_data = crud.read_course(db)
    return course_data


@router.get("/{id}", response_model=schemas.CourseResponse)
async def get_course_by_id(
        course_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read course by id

    Args:
        id (int): course id

    Returns:
        Course: course data

    Raises:
        HTTPException: course not found
    """
    course = crud.read_course_by_id(db, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="course not found")
    return course


@router.put("/LinkCourseChallenge/{course_id}/{challenge_id}", response_model=schemas.ChallengeRead)
async def update_challenge_course_id(
        course_id: int, challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Update challenge course_id by challenge id and course id

    Args:
        challenge_id: id of challenge
        course_id: id of course

    Raises:
        HTTPException: challenge not found
        HTTPException: challenge has been already linked to course
    """
    update_challenge = CRUD.challenge.update_challenge_course_id(
        db, challenge_id, course_id)
    return update_challenge
