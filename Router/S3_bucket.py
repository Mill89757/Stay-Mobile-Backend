from fastapi import APIRouter, Depends, HTTPException, status, UploadFile

# boto3 is not in requirements
import boto3
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
import CRUD.post as post_crud
from database import SessionLocal
# import CRUD.users as user_crud
import os

router = APIRouter()

S3_BUCKET_NAME = "stay-mobile-application"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# read user by user id from AWS database
@router.get("/avatar/{user_id}")
def get_user_avatar(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.read_user(db, user_id)
    file_url = user.avatar_location
    return file_url

# upload files by user id to AWS database
@router.post("/avatar/{user_id}")
def upload_user_avatar(user_id: int, file: UploadFile):

    # get the service resources
    s3 = boto3.resource("s3")

    user_id_as_file_name = "avatars/" + str(user_id) + "/" + file.filename

    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.upload_fileobj(
        file.file, user_id_as_file_name, ExtraArgs={"ACL": "public-read"}
    )
    upload_file_url = (
        f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"
    )

    return upload_file_url

# upload files to AWS database
@router.post("/default_avatars")
def upload_photos(file: UploadFile):

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(S3_BUCKET_NAME)
    new_file_name = "avatars/" + file.filename
    bucket.upload_fileobj(file.file, new_file_name, ExtraArgs={"ACL": "public-read"})

    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{new_file_name}"

    return upload_file_url

# upload challenges covers by challenge id to ASW database
@router.post("/challenge_covers/{challenge_id}")
def upload_challenger_cover(challenge_id: int, file: UploadFile):
    s3 = boto3.resource("s3")

    user_id_as_file_name = "challenge_covers/" + str(challenge_id) + "/" + file.filename

    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.upload_fileobj(
        file.file, user_id_as_file_name, ExtraArgs={"ACL": "public-read"}
    )
    upload_file_url = (
        f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"
    )

    return upload_file_url
