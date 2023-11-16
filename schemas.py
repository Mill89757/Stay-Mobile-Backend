from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# User 模型
class UserBase(BaseModel):
    firebase_uid: str
    name: str
    username: str
    email_address: Optional[str] = None
    avatar_location: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    created_time: datetime
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
    course_id: Optional[int] = None


class ChallengeRead(ChallengeBase):
    id: int
    created_time: datetime
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

    class Config:
        orm_mode = True

# Tracking 模型
class TrackingBase(BaseModel):
    created_time: Optional[datetime]
    terminated_time: Optional[datetime]
    is_terminated: Optional[bool]

class TrackingCreate(TrackingBase):
    owner_id: int
    follower_id: int
    challenge_id: int

class TrackingRead(TrackingBase):
    id: int

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
class CourseBase(BaseModel):
    course_name: str
    category: int
    description: str

class CourseCreate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int

    class Config:
        orm_mode = True
