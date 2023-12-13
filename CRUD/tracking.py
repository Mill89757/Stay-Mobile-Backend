from sqlalchemy.orm import Session
import models
import schemas

# create tracking
def create_tracking(db: Session, tracking: schemas.TrackingsRequest):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == tracking.challenge_id).first()
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

# read tracking by challenge_id
def read_tracking_by_challenge_id(db: Session, challenge_id: int):
    return db.query(models.Tracking).filter(models.Tracking.challenge_id == challenge_id).all()

# update tracking status
def update_tracking_status(db: Session, challenge_id: int,follower_id:int, tracking: schemas.TrackingsRequest):
    db_tracking = db.query(models.Tracking).filter(models.Tracking.challenge_id == challenge_id).filter(models.Tracking.follower_id == follower_id).first()
    if db_tracking is None:
        return None
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
