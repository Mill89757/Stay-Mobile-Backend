from pydantic import BaseModel
from datetime import datetime


class UsersRequest(BaseModel):
    firebase_uid: str
    name: str
    username: str
    email_address: str
    created_time: str
    avatar_location: str
    iscompleted: bool


class UsersResponse(BaseModel):
    id: int
    firebase_uid: str
    name: str
    username: str
    email_address: str
    created_time: datetime
    avatar_location: str
    iscompleted: bool

    class Config:
        orm_mode = True