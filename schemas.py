from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UsersRequest(BaseModel):
    firebase_uid: str
    name: str
    username: str
    email_address: str
    created_time:Optional[datetime] = None
    avatar_location: str
    is_completed: bool


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


class CourseResponse(BaseModel):
    id:int
    course_name:str
    category:int
    description:str

    class Config:
        orm_mode = True