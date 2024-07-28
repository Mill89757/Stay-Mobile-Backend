# pylint: disable=unused-argument

import io
import os
from datetime import datetime

import boto3
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

import CRUD.challenge as challenge_crud
import CRUD.course as course_crud
import CRUD.user as user_crud
from auth_dependencies import conditional_depends, verify_token
from database import get_db

load_dotenv()

router = APIRouter()

S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']


@router.get("/avatar/{user_id}")
def get_user_avatar(user_id: int, db: Session = Depends(get_db),
                    current_user: dict = conditional_depends(depends=verify_token)):
    """ Get user avatar from S3 by user id"""
    user = user_crud.read_user_by_id(db, user_id)
    if user and user.avatar_location:
        return user.avatar_location
    raise HTTPException(status_code=404, detail="User or avatar not found")


@router.post("/UploadAvatar/{user_id}")
def upload_user_avatar(user_id: int, file: UploadFile, db: Session = Depends(get_db)):
    """ Upload user avatar to S3

    Args:
        user_id (int): user id
        file (UploadFile): file to upload

    Returns:
        str: url of the uploaded file

    Raises:
        HTTPException: user not found
    """
    user_crud.read_user_by_id(db, user_id)  # check if user exists
    # Convert uploaded files to Pillow images
    image = Image.open(file.file).convert("RGB")  # Convert to RGB

    # Possible Resolution Adjustments - Adjust these values when needed
    max_size = (1080, 1080)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Initialize variables
    compressed_output = io.BytesIO()
    quality = 85  # Initial quality value, can be adjusted

    # Save as JPEG
    image.save(compressed_output, format="JPEG",
               quality=quality, optimize=True)
    compressed_size = compressed_output.tell()

    # If the file is still larger than 1MB, further reduce the quality
    while compressed_size > 2 * 1024 * 1024 and quality > 85:
        compressed_output.seek(0)
        quality -= 5  # Quality decrement step
        image.save(compressed_output, format="JPEG",
                   quality=quality, optimize=True)
        compressed_size = compressed_output.tell()

    compressed_output.seek(0)
    compressed_image = compressed_output.read()

    # Upload to S3 using boto3
    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}",
                        aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")
    user_id_as_file_name = f"avatars/{user_id}/{file.filename.split('.')[0]}.jpeg"
    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.put_object(Key=user_id_as_file_name, Body=compressed_image)

    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"

    return upload_file_url


@router.post("/default_avatars")
def upload_photos(file: UploadFile):
    """ Upload default avatars to S3 """
    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}",
                        aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")

    bucket = s3.Bucket(S3_BUCKET_NAME)
    new_file_name = "avatars/" + file.filename
    bucket.upload_fileobj(file.file, new_file_name)
    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{new_file_name}"

    return upload_file_url


@router.post("/Upload_challenge_covers/{challenge_id}")
def upload_challenger_cover(
        challenge_id: int, file: UploadFile, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Upload challenge cover to S3

    Args:
        challenge_id (int): challenge id
        file (UploadFile): file to upload

    Returns:
        str: url of the uploaded file

    Raises:
        HTTPException: challenge not found
    """
    challenge_crud.get_challenge(db, challenge_id)  # check if challenge exists

    # Convert uploaded files to Pillow images
    image = Image.open(file.file).convert("RGB")  # Convert to RGB

    # Possible Resolution Adjustments - Adjust these values
    max_size = (1080, 1080)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Initialize variables
    compressed_output = io.BytesIO()
    quality = 85  # Initial quality value, can be adjusted

    # Save as JPEG
    image.save(compressed_output, format="JPEG",
               quality=quality, optimize=True)
    compressed_size = compressed_output.tell()

    # If the file is still larger than 1MB, further reduce the quality
    while compressed_size > 2 * 1024 * 1024 and quality > 85:
        compressed_output.seek(0)
        quality -= 5  # Quality decrement step
        image.save(compressed_output, format="JPEG",
                   quality=quality, optimize=True)
        compressed_size = compressed_output.tell()

    compressed_output.seek(0)
    compressed_image = compressed_output.read()

    # Upload to S3 using boto3
    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}",
                        aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")
    user_id_as_file_name = f"challenge_covers/{challenge_id}/{file.filename.split('.')[0]}.jpeg"
    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.put_object(Key=user_id_as_file_name, Body=compressed_image)

    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"

    return upload_file_url


@router.post("/Upload_course_covers/{course_id}")
def upload_course_cover(
        course_id: int, file: UploadFile, db: Session = Depends(get_db),
        current_user: dict = conditional_depends(depends=verify_token)):
    """ Upload course cover to S3

    Args:
        course_id (int): course id
        file (UploadFile): file to upload

    Returns:
        str: url of the uploaded file

    Raises:
        HTTPException: course not found
    """
    course_crud.read_course_by_id(db, course_id)  # check if course exists

    # Convert uploaded files to Pillow images
    image = Image.open(file.file).convert("RGB")  # Convert to RGB

    # Possible Resolution Adjustments - Adjust these values when needed
    max_size = (1080, 1080)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Initialize variables
    compressed_output = io.BytesIO()
    quality = 85  # Initial quality value, can be adjusted

    # Save as JPEG)
    image.save(compressed_output, format="JPEG",
               quality=quality, optimize=True)
    compressed_size = compressed_output.tell()

    # If the file is still larger than 1MB, further reduce the quality
    while compressed_size > 2 * 1024 * 1024 and quality > 85:
        compressed_output.seek(0)
        quality -= 5  # Quality decrement step
        image.save(compressed_output, format="JPEG",
                   quality=quality, optimize=True)
        compressed_size = compressed_output.tell()

    compressed_output.seek(0)
    compressed_image = compressed_output.read()

    # Upload to S3 using boto3
    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}",
                        aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")
    user_id_as_file_name = f"course_covers/{course_id}/{file.filename.split('.')[0]}.jpeg"
    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.put_object(Key=user_id_as_file_name, Body=compressed_image)

    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"

    return upload_file_url


@router.post("/Upload_post_covers/")
def upload_post_cover(
    challenge_id: int, user_id: int, file: UploadFile, db: Session = Depends(get_db),
    current_user: dict = conditional_depends(depends=verify_token)
):
    """ Upload post cover to S3

    Args:
        challenge_id (int): challenge id
        user_id (int): user id
        file (UploadFile): file to upload

    Returns:
        str: url of the uploaded file

    Raises:
        HTTPException: challenge not found
        HTTPException: user not found

    usage example: http://Upload_post_covers?challenge_id=1&user_id=1
    """
    def get_s3_resource():
        return boto3.resource(
            "s3",
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )

    def compress_image(file: UploadFile, max_size=(1080, 1080), initial_quality=85):
        image = Image.open(file.file).convert("RGB")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        compressed_output = io.BytesIO()

        quality = initial_quality
        image.save(compressed_output, format="JPEG",
                   quality=quality, optimize=True)
        compressed_size = compressed_output.tell()

        while compressed_size > 2 * 1024 * 1024 and quality > 85:
            compressed_output.seek(0)
            quality -= 5
            image.save(compressed_output, format="JPEG",
                       quality=quality, optimize=True)
            compressed_size = compressed_output.tell()

        compressed_output.seek(0)
        return compressed_output.read()

    def upload_to_s3(s3_resource, bucket_name, key, data):
        bucket = s3_resource.Bucket(bucket_name)
        bucket.put_object(Key=key, Body=data)
        return f"https://{bucket_name}.s3.amazonaws.com/{key}"

    challenge_crud.get_challenge(db, challenge_id)  # check if challenge exists
    user_crud.read_user_by_id(db, user_id)  # check if user exists

    compressed_image = compress_image(file)

    s3 = get_s3_resource()
    created_time = datetime.now().strftime("%Y%m%d%H%M%S")
    post_id_as_file_name = \
        f"post_covers/{challenge_id}/{created_time}_{user_id}_{file.filename.split('.')[0]}.jpeg"

    upload_file_url = upload_to_s3(
        s3, S3_BUCKET_NAME, post_id_as_file_name, compressed_image)

    return upload_file_url
