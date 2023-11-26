from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
import boto3
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
import CRUD.post as post_crud
from database import SessionLocal
import CRUD.user as user_crud
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

S3_BUCKET_NAME = "stay-mobile-application"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/avatar/{user_id}")
def get_user_avatar(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.read_user_by_id(db, user_id)
    if user and user.avatar_location:
        return user.avatar_location
    raise HTTPException(status_code=404, detail="User or avatar not found")


@router.post("/UploadAvatar/{user_id}")
def upload_user_avatar(user_id: int, file: UploadFile):
    
    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")

    user_id_as_file_name = "avatars/" + str(user_id) + "/" + file.filename
    
    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.upload_fileobj(
        file.file, user_id_as_file_name
    )
    upload_file_url = (
        f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"
    )

    return upload_file_url


@router.post("/default_avatars")
def upload_photos(file: UploadFile):

    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")

    bucket = s3.Bucket(S3_BUCKET_NAME)
    new_file_name = "avatars/" + file.filename
    bucket.upload_fileobj(file.file, new_file_name)
    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{new_file_name}"

    return upload_file_url


@router.post("/challenge_covers/{challenge_id}")
def upload_challenger_cover(challenge_id: int, file: UploadFile):

    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")

    user_id_as_file_name = "challenge_covers/" + str(challenge_id) + "/" + file.filename

    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.upload_fileobj(
        file.file, user_id_as_file_name
    )
    upload_file_url = (
        f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"
    )

    return upload_file_url
