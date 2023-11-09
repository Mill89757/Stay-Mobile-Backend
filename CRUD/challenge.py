# wait for schemas.py 
from sqlalchemy.orm import Session
import models
import database

# Create a new challenge
def create_challenge(db: Session, challenge: schemas.ChallengeCreate):
    db_challenge = models.Challenge(**challenge.dict())
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

# Read a challenge by ID
def get_challenge(db: Session, challenge_id: int):
    return db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()

# Read all challenges
def get_challenges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Challenge).offset(skip).limit(limit).all()

# Update a challenge
def update_challenge(db: Session, challenge_id: int, challenge: schemas.ChallengeUpdate):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not db_challenge:
        return None
    for var, value in vars(challenge).items():
        setattr(db_challenge, var, value) if value else None
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

# Delete a challenge
def delete_challenge(db: Session, challenge_id: int):
    db_challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if db_challenge is None:
        return None
    db.delete(db_challenge)
    db.commit()
    return db_challenge
