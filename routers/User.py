from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud.User as crud
from database import SessionLocal
from typing import List

router = APIRouter(prefix="/user")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", status_code=status.HTTP_201_CREATED)
def create_users(user: schemas.UsersRequest, db: Session = Depends(get_db)):
    user = crud.create_user(db, user)
    return user

@router.get("", response_model=List[schemas.UsersResponse])
def get_users(db: Session = Depends(get_db)):
    users = crud.read_users(db)
    return users

@router.put("/{id}")
def update_user(id: int, user: schemas.UsersRequest, db: Session = Depends(get_db)):
    user = crud.update_user(db, id, user)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_user(id: int, db: Session = Depends(get_db)):
    res = crud.delete_user(db, id)
    if res is None:
        raise HTTPException(status_code=404, detail="user not found")