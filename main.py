from functools import lru_cache
from typing import Union

from fastapi import FastAPI, Depends
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

import schemas

app = FastAPI()


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
import crud
from database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.get("/user")
# def get_user_data(db: Session = Depends(get_db)):
#     user_data = crud.read_user(db)
#     return user_data

# @app.post("/user", status_code=status.HTTP_201_CREATED)
# def create_users(user: schemas.UsersRequest, db: Session = Depends(get_db)):
#     user = crud.create_user(db, user)
#     return user

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    print(f"{repr(exc)}")
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

@app.get("/")
def read_root():
    return "Welcome to Stay - Mobile API"

# @app.get("/course")
# def get_course_data(db: Session = Depends(get_db)):
#     course_data = crud.read_course(db)
#     return course_data
