from sqlalchemy.orm import Session
import models



def read_user(db: Session):
    return db.query(models.User).all()

   