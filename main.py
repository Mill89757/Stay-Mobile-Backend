from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal
from Router.challenge import router as challenge_router 
from Router.post import router as post_router
from Router.post_content import router as post_content_router
from Router.S3_bucket import router as S3_bucket_router
from Router.post_reaction import router as post_reaction_router
from Router.user_reaction_log import router as user_reaction_log_router

#connect to router
from Router.user import router as user_router 
from Router.course import router as course_router
from Router.tracking import router as tracking_router

# initialize backend application
# create an instance object from FastAPI 
app = FastAPI()
app.include_router(user_router)
app.include_router(course_router)
app.include_router(tracking_router)
app.include_router(challenge_router)
app.include_router(post_router)
app.include_router(post_content_router)
app.include_router(S3_bucket_router)
app.include_router(post_reaction_router)
app.include_router(user_reaction_log_router)

# Using dependency to create an independent database connection per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CORS, communicates with frontend running indifferent ports/origins
# configure "http://localhost:3000" as the frontend origins
# allow all methods and all headers
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
# override the default exception handlers
# return HTTP responses with error codes to the client in plain text format
# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(exc):
#     print(f"{repr(exc)}")
#     return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    print(f"{repr(exc)}")
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

# define route "/" operation & function
@app.get("/")
def read_root():
    return "Welcome to Stay - Mobile API"

