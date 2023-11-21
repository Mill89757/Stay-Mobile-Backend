from sqlalchemy.orm import Session
import models

# Read all courses
def read_course(db: Session):
    return db.query(models.Course).all()

# Read course by id
def read_course_by_id(db: Session, id: int):
    return db.query(models.Course).filter(models.Course.id == id).first()