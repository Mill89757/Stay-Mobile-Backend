from functools import lru_cache
from typing import Union
from fastapi import FastAPI, Depends
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.orm import Session
from database import SessionLocal
from Router.challenge import router as challenge_router 
from Router.post import router as post_router
from Router.post_content import router as post_content_router
from Router.S3_bucket import router as S3_bucket_router

#connect to router
from Router.user import router as user_router 
from Router.course import router as course_router
app = FastAPI()
app.include_router(user_router)
app.include_router(course_router)
app.include_router(challenge_router)
app.include_router(post_router)
app.include_router(post_content_router)
app.include_router(S3_bucket_router)

# Testing 2

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    print(f"{repr(exc)}")
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

@app.get("/")
def read_root():
    return "Welcome to Stay - Mobile API"

