from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from Router.automation import router as automation_router
from Router.blocked_user_list import router as blocked_user_router
from Router.challenge import router as challenge_router
from Router.course import router as course_router
from Router.expo_push_token import router as expo_push_token_router
from Router.post import router as post_router
from Router.post_content import router as post_content_router
from Router.post_reaction import router as post_reaction_router
from Router.pushNotification import router as send_notification
from Router.S3_bucket import router as S3_bucket_router
from Router.tracking import router as tracking_router
from Router.user import router as user_router
from Router.user_reaction_log import router as user_reaction_log_router

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
app.include_router(automation_router)
app.include_router(expo_push_token_router)
app.include_router(send_notification)
app.include_router(blocked_user_router)


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
async def http_exception_handler(exc: StarletteHTTPException):
    """ Handle HTTPException """
    print(f"{repr(exc)}")
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.get("/")
def read_root():
    """ Welcome message """
    return "Welcome to Stay - Mobile API"
