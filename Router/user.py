from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
import schemas
from database import SessionLocal
import CRUD.user as crud

router = APIRouter(prefix="/user")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create user
@router.post("", status_code=status.HTTP_201_CREATED)
def create_users(user: schemas.UsersRequest, db: Session = Depends(get_db)):
    user = crud.create_user(db, user)
    return user

#read all users
@router.get("", response_model=List[schemas.UsersResponse])
def get_users(db: Session = Depends(get_db)):
    users = crud.read_users(db)
    return users

#read user by id
@router.get("/{id}")
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = crud.read_user_by_id(db, id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user

#update user
@router.put("/{id}")
def update_user(id: int, user: schemas.UsersRequest, db: Session = Depends(get_db)):
    user = crud.update_user(db, id, user)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user

#delete user
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_user(id: int, db: Session = Depends(get_db)):
    res = crud.delete_user(db, id)
    if res is None:
        raise HTTPException(status_code=404, detail="user not found")