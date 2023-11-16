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
# import crud
from database import SessionLocal
# from CRUD import challenge
from Router.challenge import router as challenge_router 
from Router.post import router as post_router
from Router.tracking import router as tracking_router

app = FastAPI()
app.include_router(tracking_router)
app.include_router(challenge_router)
app.include_router(post_router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    print(f"{repr(exc)}")
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

@app.get("/")
def read_root():
    return "Welcome to Stay - Mobile API"

