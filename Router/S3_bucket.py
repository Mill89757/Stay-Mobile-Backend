from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
import boto3
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
import CRUD.post as post_crud
from database import SessionLocal
import CRUD.user as user_crud
import CRUD.challenge as challenge_crud
import CRUD.course as course_crud
import os
from PIL import Image
import io
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials, auth, initialize_app
from auth_dependencies import verify_token, conditional_depends
from dotenv import load_dotenv
# load env file
load_dotenv()

router = APIRouter()

S3_BUCKET_NAME = "stay-mobile-application"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# read user from AWS database by user id 
@router.get("/avatar/{user_id}")
def get_user_avatar(user_id: int, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    user = user_crud.read_user_by_id(db, user_id)
    if user and user.avatar_location:
        return user.avatar_location
    raise HTTPException(status_code=404, detail="User or avatar not found")

# upload files into AWS database by user id
@router.post("/UploadAvatar/{user_id}")
def upload_user_avatar(user_id: int, file: UploadFile, db: Session = Depends(get_db)):
    """Upload user avatar to S3
    
    Args:
        user_id (int): user id
        file (UploadFile): file to upload
    
    Returns:
        str: url of the uploaded file
    
    Raises:
        HTTPException: user not found
    """
    user_crud.read_user_by_id(db, user_id)# check if user exists
   # 将上传的文件转换为Pillow图像
    image = Image.open(file.file).convert("RGB")  # 转换为RGB

    # 可能的分辨率调整 - 根据需要调整这些值
    max_size = (1080, 1080)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # 初始化变量
    compressed_output = io.BytesIO()
    quality = 85  # 初始质量值，可以调整

    # 保存为JPEG
    image.save(compressed_output, format="JPEG", quality=quality, optimize=True)
    compressed_size = compressed_output.tell()

    # 如果文件仍然大于1MB，进一步降低质量
    while compressed_size > 2 * 1024 * 1024 and quality > 85:
        compressed_output.seek(0)
        quality -= 5  # 质量递减步长
        image.save(compressed_output, format="JPEG", quality=quality, optimize=True)
        compressed_size = compressed_output.tell()

    compressed_output.seek(0)
    compressed_image = compressed_output.read()

    # 使用 boto3 上传到 S3
    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")
    user_id_as_file_name = f"avatars/{user_id}/{file.filename.split('.')[0]}.jpeg"
    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.put_object(Key=user_id_as_file_name, Body=compressed_image)

    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"

    return upload_file_url



@router.post("/default_avatars")
def upload_photos(file: UploadFile):

    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")

    bucket = s3.Bucket(S3_BUCKET_NAME)
    new_file_name = "avatars/" + file.filename
    bucket.upload_fileobj(file.file, new_file_name)
    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{new_file_name}"

    return upload_file_url


@router.post("/Upload_challenge_covers/{challenge_id}")
def upload_challenger_cover(challenge_id: int, file: UploadFile, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """Upload challenge cover to S3
    
    Args:
        challenge_id (int): challenge id
        file (UploadFile): file to upload
    
    Returns:
        str: url of the uploaded file
        
    Raises:
        HTTPException: challenge not found
    """
    challenge_crud.get_challenge(db, challenge_id)# check if challenge exists

    # 将上传的文件转换为Pillow图像
    image = Image.open(file.file).convert("RGB")  # 转换为RGB

    # 可能的分辨率调整 - 根据需要调整这些值
    max_size = (1080, 1080)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # 初始化变量
    compressed_output = io.BytesIO()
    quality = 85  # 初始质量值，可以调整

    # 保存为JPEG
    image.save(compressed_output, format="JPEG", quality=quality, optimize=True)
    compressed_size = compressed_output.tell()

    # 如果文件仍然大于1MB，进一步降低质量
    while compressed_size > 2 * 1024 * 1024 and quality > 85:
        compressed_output.seek(0)
        quality -= 5  # 质量递减步长
        image.save(compressed_output, format="JPEG", quality=quality, optimize=True)
        compressed_size = compressed_output.tell()

    compressed_output.seek(0)
    compressed_image = compressed_output.read()

    # 使用 boto3 上传到 S3
    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")
    user_id_as_file_name = f"challenge_covers/{challenge_id}/{file.filename.split('.')[0]}.jpeg"
    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.put_object(Key=user_id_as_file_name, Body=compressed_image)

    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"

    return upload_file_url



@router.post("/Upload_course_covers/{course_id}")
def upload_course_cover(course_id: int, file: UploadFile, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """Upload course cover to S3
    
    Args:
        course_id (int): course id
        file (UploadFile): file to upload
    
    Returns:
        str: url of the uploaded file
        
    Raises:
        HTTPException: course not found
    """
    course_crud.read_course_by_id(db, course_id)# check if course exists

    # 将上传的文件转换为Pillow图像
    image = Image.open(file.file).convert("RGB")  # 转换为RGB

    # 可能的分辨率调整 - 根据需要调整这些值
    max_size = (1080, 1080)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # 初始化变量
    compressed_output = io.BytesIO()
    quality = 85  # 初始质量值，可以调整

    # 保存为JPEG
    image.save(compressed_output, format="JPEG", quality=quality, optimize=True)
    compressed_size = compressed_output.tell()

    # 如果文件仍然大于1MB，进一步降低质量
    while compressed_size > 2 * 1024 * 1024 and quality > 85:
        compressed_output.seek(0)
        quality -= 5  # 质量递减步长
        image.save(compressed_output, format="JPEG", quality=quality, optimize=True)
        compressed_size = compressed_output.tell()

    compressed_output.seek(0)
    compressed_image = compressed_output.read()

    # 使用 boto3 上传到 S3
    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")
    user_id_as_file_name = f"course_covers/{course_id}/{file.filename.split('.')[0]}.jpeg"
    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.put_object(Key=user_id_as_file_name, Body=compressed_image)

    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id_as_file_name}"

    return upload_file_url



#post cover
@router.post("/Upload_post_covers/")#用challenge_id来标记post
def upload_post_cover(challenge_id: int, user_id: int, file: UploadFile, db: Session = Depends(get_db),current_user: dict = conditional_depends(depends=verify_token)):
    """Upload post cover to S3
    
    Args:
        challenge_id (int): challenge id
        user_id (int): user id
        file (UploadFile): file to upload
        
    Returns:
        str: url of the uploaded file
        
    Raises:
        HTTPException: challenge not found
        HTTPException: user not found
    """
    challenge_crud.get_challenge(db, challenge_id)# check if challenge exists
    user_crud.read_user_by_id(db, user_id)# check if user exists

    # usage example: http://Upload_post_covers?challenge_id=1&user_id=1

    # 将上传的文件转换为Pillow图像
    image = Image.open(file.file).convert("RGB")  # 转换为RGB

    # 可能的分辨率调整 - 根据需要调整这些值
    max_size = (1080, 1080)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # 初始化变量
    compressed_output = io.BytesIO()
    quality = 85  # 初始质量值，可以调整

    # 保存为JPEG
    image.save(compressed_output, format="JPEG", quality=quality, optimize=True)
    compressed_size = compressed_output.tell()

    # 如果文件仍然大于1MB，进一步降低质量
    while compressed_size > 2 * 1024 * 1024 and quality > 85:
        compressed_output.seek(0)
        quality -= 5  # 质量递减步长
        image.save(compressed_output, format="JPEG", quality=quality, optimize=True)
        compressed_size = compressed_output.tell()

    compressed_output.seek(0)
    compressed_image = compressed_output.read()

    # 使用 boto3 上传到 S3
    s3 = boto3.resource("s3", aws_access_key_id=f"{os.environ['AWS_ACCESS_KEY_ID']}", aws_secret_access_key=f"{os.environ['AWS_SECRET_ACCESS_KEY']}")
    # post_id_as_file_name = f"post_covers/{challenge_id}/{file.filename.split('.')[0]}.jpeg"
    from datetime import datetime
    created_time = datetime.now().strftime("%Y%m%d%H%M%S")
    post_id_as_file_name = f"post_covers/{challenge_id}/{created_time}_{user_id}_{file.filename.split('.')[0]}.jpeg"
    bucket = s3.Bucket(S3_BUCKET_NAME)
    bucket.put_object(Key=post_id_as_file_name, Body=compressed_image)

    upload_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{post_id_as_file_name}"

    return upload_file_url