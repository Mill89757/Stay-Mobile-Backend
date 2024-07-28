# pylint: disable=unused-argument

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import CRUD.tracking as crud
import schemas
from auth_dependencies import conditional_depends, verify_token
from database import get_db

router = APIRouter(
    prefix="/tracking"
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_tracking(
        tracking: schemas.TrackingsRequest, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Create tracking

    Args:
        tracking: tracking record

    Returns:
        tracking record

    Raises:
        HTTPException: challenge not found
        HTTPException: follower not found
        HTTPException: This user is not the owner of this challenge
    """
    tracking = crud.create_tracking(db, tracking)
    return tracking


@router.get("/challenge/{challenge_id}",
            response_model=List[schemas.TrackingsResponse])
def get_tracking_by_challenge_id(
        challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read tracking by challenge_id

    Args: 
        challenge_id: id of challenge

    Returns: 
        tracking record

    Raises:
        HTTPException: challenge not found
        HTTPException: no tracking found
    """
    tracking = crud.read_tracking_by_challenge_id(db, challenge_id)
    if tracking is None:
        raise HTTPException(status_code=404, detail="challenge not found")
    return tracking


@router.get("/challenge/follower/{challenge_id}")
def get_follower_by_challenge_id(
        challenge_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read all follower avatar_location by challenge_id, is_terminated is False/True

    Args:
        challenge_id: id of challenge

    Returns:
        list of follower avatar_location

    Raises:
        HTTPException: challenge not found
    """

    tracking = crud.read_follower_by_challenge_id(db, challenge_id)
    if tracking is None:
        raise HTTPException(status_code=404, detail="challenge not found")
    return tracking


@router.get("/follower/data/{follower_id}")
def get_activated_tracking_challenge_data_by_follower_id(
        follower_id: int, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Read all activated tracking by user_id

    Args:
        follower_id: id of follower

    Returns:
        list of tracking record

    Raises:
        HTTPException: follower not found
    """
    tracking = crud.read_activated_tracking_challenge_data_by_follower_id(
        db, follower_id)
    if tracking is None:
        raise HTTPException(status_code=404, detail="follower not found")
    return tracking


@router.put("/")
def update_tracking_status(
        challenge_id: int, follower_id: int, tracking: schemas.TrackingsResponse,
        db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Update tracking status

    Args:
        challenge_id: id of challenge
        follower_id: id of follower
        tracking: tracking record

    Returns:
        tracking record

    Raises:
        HTTPException: challenge not found
        HTTPException: follower not found
        HTTPException: tracking not found
    """
    res = crud.update_tracking_status(db, challenge_id, follower_id, tracking)
    return res


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_tracking(tracking_id: int, db: Session = Depends(get_db),
                    current_user: dict = conditional_depends(depends=verify_token)):
    """ Delete tracking by tracking id"""
    res = crud.delete_tracking(db, tracking_id)
    if res is None:
        raise HTTPException(status_code=404, detail="tracking not found")
