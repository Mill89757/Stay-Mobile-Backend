from sqlalchemy.orm import Session
import models
import schemas
from CRUD.user import read_user_by_id
from CRUD.challenge import get_challenge
from fastapi import HTTPException, status

# create tracking
def create_tracking(db: Session, tracking: schemas.TrackingsRequest):
    """create tracking
    
    Args:
        tracking: tracking record
        
    Returns:
        tracking record
    
    Raises:
        HTTPException: challenge not found
        HTTPException: follower not found
        HTTPException: This user is not the owner of this challenge
    """
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == tracking.challenge_id).first()
    if db_challenge.challenge_owner_id != tracking.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user is not the owner of this challenge")
    if db_challenge:  # avoid same record repeat in this table
        db_tracking = models.Tracking(created_time=tracking.created_time,
                                      terminated_time=tracking.terminated_time,
                                      is_terminated=tracking.is_terminated,
                                      owner_id=tracking.owner_id,
                                      follower_id=tracking.follower_id,
                                      challenge_id=db_challenge.id)
        db.add(db_tracking)
        db.commit()
        db.refresh(db_tracking)
        return db_tracking
    else:
        return None

def read_tracking_by_challenge_id(db: Session, challenge_id: int):
    """read tracking by challenge_id

    Args: 
        challenge_id: id of challenge

    Returns: 
        tracking record
    
    Raises:
        HTTPException: challenge not found
        HTTPException: no tracking found
    """
    get_challenge(db, challenge_id)# check if challenge_id exists
    result = db.query(models.Tracking).filter(models.Tracking.challenge_id == challenge_id).all()
    return result

def read_follower_by_challenge_id(db: Session, challenge_id: int):
    """read all follower avatar_location by challenge_id, is_terminated is False/True

    Args:
        challenge_id: id of challenge

    Returns:
        list of follower avatar_location

    Raises:
        HTTPException: challenge not found
    """
    get_challenge(db, challenge_id)# check if challenge_id exists
    challenge_tracking = db.query(models.Challenge, models.Tracking)\
        .join(models.Tracking, models.Challenge.id == models.Tracking.challenge_id)\
        .order_by(models.Tracking.created_time).filter(models.Tracking.challenge_id == challenge_id).limit(10).all()
    follower_id = [record[1].follower_id for record in challenge_tracking]
    result = []
    for id in follower_id:
        follower_user = db.query(models.User).filter(models.User.id == id).first()
        follower_avatar = follower_user.avatar_location
        result.append(follower_avatar)
    return result

def read_activated_tracking_challenge_data_by_follower_id(db: Session, follower_id: int):
    """
    read all activated tracking by user_id

    Args:
        follower_id: id of follower
        
    Returns:
        list of tracking record
    
    Raises:
        HTTPException: follower not found
    """
    read_user_by_id(db, follower_id)# check if follower_id exists
    follower = db.query(models.Tracking).filter(models.Tracking.follower_id == follower_id).first()
    if follower is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user haven't followed any challenge")
    db_activated_tracking = db.query(models.Tracking).filter(
        models.Tracking.follower_id == follower_id).filter(models.Tracking.is_terminated == False).all()
    result = []
    for tracking_record in db_activated_tracking:
        challenge_owner = read_user_by_id(db, tracking_record.owner_id)
        challenge = get_challenge(db, tracking_record.challenge_id)
        result.append({
            "id": tracking_record.id,
            "created_time": tracking_record.created_time,
            "terminated_time": tracking_record.terminated_time,
            "is_terminated": tracking_record.is_terminated,
            "follower_id": tracking_record.follower_id,
            "challenge_id": tracking_record.challenge_id,
            "challenge_title": challenge.title,
            "challenge_description": challenge.description,
            "challenge_duration": challenge.duration,
            "challenge_breaking_days": challenge.breaking_days,
            "challenge_category": challenge.category,
            "challenge_created_time": challenge.created_time,
            "challenge_cover_location": challenge.cover_location,
            "challenge_owner_name": challenge_owner.name,
            "challenge_owner_avatar_location": challenge_owner.avatar_location,
        })
    return result

# update tracking status
def update_tracking_status(db: Session, challenge_id: int,follower_id:int, tracking: schemas.TrackingsRequest):
    """update tracking status

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
    get_challenge(db, challenge_id)# check if challenge_id exists
    read_user_by_id(db, follower_id)# check if follower_id exists
    db_tracking = db.query(models.Tracking).filter(models.Tracking.challenge_id == challenge_id).filter(models.Tracking.follower_id == follower_id).first()
    if db_tracking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking not found")
    db.query(models.Tracking).filter(models.Tracking.challenge_id == challenge_id).filter(models.Tracking.follower_id == follower_id).update(
        {
            "created_time": tracking.created_time,
            "terminated_time": tracking.terminated_time,
            "is_terminated": tracking.is_terminated,
            "owner_id": tracking.owner_id,
            "follower_id": tracking.follower_id,
            "challenge_id": tracking.challenge_id,
        }
    )
    db.commit()
    db.refresh(db_tracking)
    return db_tracking

# delete tracking by id
def delete_tracking(db: Session, id: int):
    db_tracking = db.query(models.Tracking).filter(models.Tracking.id == id).first()
    if db_tracking is None:
        return None
    db.query(models.Tracking).filter(models.Tracking.id == id).delete()
    db.commit()
    return True
