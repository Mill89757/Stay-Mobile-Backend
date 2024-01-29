from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# schemas.py is used to build pydantic models, which controls data validation, conversion, documentation classes and instances
# schemas.py is used to build pydantic models, which controls data validation, conversion, documentation classes and instances
# define and validate whether the incoming data structure matches as expected

# User 模型
class UsersRequest(BaseModel):
    firebase_uid: str
    name: str
    username: str
    email_address: str
    created_time: Optional[datetime] = None
    avatar_location: Optional[str] = None
    is_completed: Optional[bool] = False#默认false
    user_timezone: str

class UsersResponse(BaseModel):
    id: int
    firebase_uid: str
    name: str
    username: str
    email_address: str
    created_time:  Optional[datetime] = None
    avatar_location: str
    is_completed: bool
    user_timezone: str

    class Config:
        orm_mode = True


# Challenge 模型
class ChallengeBase(BaseModel):
    title: str
    description: str
    duration: Optional[int] = None
    breaking_days: Optional[int] = None
    is_public: bool = False
    is_completed: Optional[bool] = False
    is_completed: Optional[bool] = False
    created_time:Optional[datetime] = None
    category: Optional[int] = None
    cover_location: Optional[str] = None
    days_left: Optional[int] = None
    is_group_challenge: bool

class ChallengeCreate(BaseModel):
    title: str
    description: str
    duration: Optional[int] = None
    breaking_days: Optional[int] = None
    is_public: bool = False
    category: Optional[int] = None
    cover_location: Optional[str] = None
    
    challenge_owner_id: int
    # course_id: Optional[int] = None

class ChallengeRead(ChallengeBase):
    id: int
    title: str
    category: int
    duration: int
    cover_location: str
    finished_time: Optional[datetime] = None
    is_completed: bool
    challenge_owner_id: int
    course_id: Optional[int] = None

    class Config:
        orm_mode = True

#Group Challenge 模型
class GroupChallengeMembersBase(BaseModel):
    challenge_id: int
    user_id: int
    days_left: Optional[int] = None
    breaking_days_left: int
    is_challenge_finished: bool

class GroupChallengeMembersCreate(GroupChallengeMembersBase):
    breaking_days_left: int
    days_left: Optional[int] = None
    is_challenge_finished: bool

class GroupChallengeMembersRead(GroupChallengeMembersBase):
    breaking_days_left: int
    days_left: Optional[int] = None
    is_challenge_finished: bool

    class Config:
        orm_mode = True

class ChallengeWithBreakingDays(ChallengeRead):  # Assuming ChallengeRead is your base schema for reading challenges
    id: int
    title: str
    description: str
    duration: int
    breaking_days: int
    is_public: bool
    category: int
    created_time: datetime
    finished_time: Optional[datetime] = None
    cover_location: str
    challenge_owner_id: int
    course_id: Optional[int] = None
    is_completed: bool
    days_left: int
    is_group_challenge: bool
    breaking_days_left: int


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
    image_location: Optional[str] = None
    #when creating a post, the image_location is optional, because the user may not upload an image
    #create post will create a post and a post_content at the same time
    #if user wants to upload an image, the image_location will be updated in the post_content table

class PostRead(PostBase):
    id: int
    user_id: int
    challenge_id: int
    start_time: datetime
    end_time: datetime
    written_text: str
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
"""class ReactionBase(BaseModel):
    emoji_type: int
    amount: int

class ReactionCreate(ReactionBase):
    post_id: int
    user_id: int

class ReactionRead(ReactionBase):
    id: int

    class Config:
        orm_mode = True
"""
# Course 模型
class CourseResponse(BaseModel):
    id:int
    course_name:str
    category:int
    description:str
    cover_location:str
    source_link:str
    short_intro:str

    class Config:
        orm_mode = True

# User reaction log model
class UserReactionLogBase(BaseModel):
    created_datetime: datetime
    is_cancelled:bool

class UserReactionLogCreate(UserReactionLogBase):
    user_id:int
    post_id:int
    emoji_image:str

class UserReactionLogRead(UserReactionLogBase):
    log_id:int
    user_id:int
    post_id:int
    emoji_image:str
    
    class Config:
        orm_mode = True

# emoji 模型
class EmojiBase(BaseModel):
    name: str

# post reaction 模型
class PostReactionBase(BaseModel):
    count: int

class PostReactionCreate(PostReactionBase):
    post_id: int
    emoji_image: str

    class Config:
        orm_mode = True


#discover challenge 模型
class ChallengesDiscover(BaseModel):
    id: int
    cover_location: str
    title: str
    owner_id: int
    owner_avatar: str
    follower_avatars: list
    challenge_process: float

    class Config:
        orm_mode = True

#group challenge member模型
class GroupChallengesMember(BaseModel):
    user_id: int
    breaking_days_left: int
    days_left: int
    is_challenge_finished: bool
    challenge_id: int
    user_name: str
    challenge_category: int

    class Config:
        orm_mode = True
