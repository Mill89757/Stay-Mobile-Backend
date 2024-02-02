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
from Router.post_reaction import router as post_reaction_router
from Router.user_reaction_log import router as user_reaction_log_router
from Router.expo_push_token import router as expo_push_token_router
from Router.pushNotification import router as send_notification
#connect to router
from Router.user import router as user_router 
from Router.course import router as course_router

# initialize backend application
# create an instance object from FastAPI 
app = FastAPI()
app.include_router(user_router)
app.include_router(course_router)
app.include_router(challenge_router)
app.include_router(post_router)
app.include_router(post_content_router)
app.include_router(S3_bucket_router)
app.include_router(post_reaction_router)
app.include_router(user_reaction_log_router)
app.include_router(expo_push_token_router)
app.include_router(send_notification)

# Testing 2
# Using dependency to create an independent database connection per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CORS, communicates with fronend running indifferent ports/orgins
# configure "http://localhost:3000" as the frontend origins
# allow all methods and all headers
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
# override the default exception handlers
# return HTTP responses with error codes to the client in plain text format
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    print(f"{repr(exc)}")
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

# define route "/" operation & function
@app.get("/")
def read_root():
    return "Welcome to Stay - Mobile API"

