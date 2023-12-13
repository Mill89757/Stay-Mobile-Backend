from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# schemas.py is used to build pydantic models, which controls data validation, conversion, documentation classes and instances
# define and validate whether the incoming data structure matches as expected

# User 模型
class UsersRequest(BaseModel):
    firebase_uid: str
    name: str
    username: str
    email_address: str
    created_time:Optional[datetime] = None
    avatar_location: Optional[str] = None
    is_completed: Optional[bool] = False#默认false

class UsersResponse(BaseModel):
    id: int
    firebase_uid: str
    name: str
    username: str
    email_address: str
    created_time: datetime
    avatar_location: str
    is_completed: bool

    class Config:
        orm_mode = True


# Challenge 模型
class ChallengeBase(BaseModel):
    title: str
    description: str
    duration: Optional[int] = None
    breaking_days: Optional[int] = None
    is_public: bool = False
    is_finished: Optional[bool] = False
    created_time:Optional[datetime] = None
    category: Optional[int] = None
    cover_location: Optional[str] = None
    days_left: Optional[int] = None
    breaking_days_left: Optional[int] = None

class ChallengeCreate(BaseModel):
    title: str
    description: str
    duration: Optional[int] = None
    breaking_days: Optional[int] = None
    is_public: bool = False
    category: Optional[int] = None
    cover_location: Optional[str] = None
    days_left: Optional[int] = None
    breaking_days_left: Optional[int] = None
    user_id: int
    # course_id: Optional[int] = None

class ChallengeRead(ChallengeBase):
    id: int
    title: str
    category: int
    duration: int
    days_left: int
    breaking_days_left: int
    cover_location: str
    finished_time: Optional[datetime] = None
    is_finished: bool
    user_id: int
    course_id: Optional[int] = None

    class Config:
        orm_mode = True

# Post 模型
class PostBase(BaseModel):
    created_time: Optional[datetime] = None
    start_time: datetime
    end_time: datetime
    written_text: str

class PostCreate(BaseModel):
    user_id: int
    challenge_id: int
    start_time: datetime
    end_time: datetime
    written_text: str

class PostRead(PostBase):
    id: int
    user_id: int
    challenge_id: int
    start_time: datetime
    end_time: datetime
    written_text: str

    class Config:
        orm_mode = True

# Tracking 模型
class TrackingsRequest(BaseModel):
    created_time: Optional[datetime] = None
    terminated_time: Optional[datetime] = None
    is_terminated: Optional[bool] = False
    owner_id: int
    follower_id: int
    challenge_id: int

class TrackingsResponse(BaseModel):
    id: int
    created_time: datetime
    terminated_time: Optional[datetime] = None
    is_terminated: bool
    owner_id: int
    follower_id: int
    challenge_id: int

    class Config:
        orm_mode = True

# PostContent 模型
class PostContentBase(BaseModel):
    video_location: Optional[str]
    image_location: Optional[str]
    voice_location: Optional[str]

class PostContentCreate(PostContentBase):
    post_id: int

class PostContentRead(PostContentBase):
    id: int
    post_id: int

    class Config:
        orm_mode = True

# Reaction 模型
class ReactionBase(BaseModel):
    emoji_type: int
    amount: int

class ReactionCreate(ReactionBase):
    post_id: int
    user_id: int

class ReactionRead(ReactionBase):
    id: int

    class Config:
        orm_mode = True

# Course 模型
class CourseResponse(BaseModel):
    id:int
    course_name:str
    category:int
    description:str
    cover_location:str

    class Config:
        orm_mode = True
