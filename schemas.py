"""
schemas.py is used to build pydantic models, which controls data validation,
conversion, documentation classes and instances

define and validate whether the incoming data structure matches as expected
"""
# pylint: disable=too-few-public-methods, missing-class-docstring

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UsersRequest(BaseModel):
    """
    Schema for user request data.

    Attributes:
        firebase_uid (str): The Firebase UID of the user.
        name (str): The name of the user.
        username (str): The username of the user.
        email_address (str): The email address of the user.
        created_time (Optional[datetime]): The creation time of the user record.
        avatar_location (Optional[str]): The location of the user's avatar.
        is_completed (Optional[bool]): Whether the user profile is completed. Defaults to False.
        user_timezone (str): The timezone of the user.
        is_blocked (Optional[bool]): Whether the user is blocked. Defaults to False.
    """
    firebase_uid: str
    name: str
    username: str
    email_address: str
    created_time: Optional[datetime] = None
    avatar_location: Optional[str] = None
    is_completed: Optional[bool] = False
    user_timezone: str
    is_blocked: Optional[bool] = False


class UsersResponse(BaseModel):
    """
    Schema for user response data.

    Attributes:
        id (int): The unique identifier of the user.
        firebase_uid (str): The Firebase UID of the user.
        name (str): The name of the user.
        username (str): The username of the user.
        email_address (str): The email address of the user.
        created_time (Optional[datetime]): The creation time of the user record.
        avatar_location (str): The location of the user's avatar.
        is_completed (bool): Whether the user profile is completed.
        user_timezone (str): The timezone of the user.
        is_blocked (Optional[bool]): Whether the user is blocked. Defaults to False.
    """
    id: int
    firebase_uid: str
    name: str
    username: str
    email_address: str
    created_time:  Optional[datetime] = None
    avatar_location: str
    is_completed: bool
    user_timezone: str
    is_blocked: Optional[bool] = False

    class Config:
        orm_mode = True


class ChallengeBase(BaseModel):
    """ 
    Schema for challenge model data.

    Attributes:
        title (str): The title of the challenge.
        description (str): The description of the challenge.
        duration (Optional[int]): The duration of the challenge.
        breaking_days (Optional[int]): The breaking days of the challenge.
        is_public (bool): Whether the challenge is public. Defaults to False.
        is_completed (Optional[bool]): Whether the challenge is completed. Defaults to False.
        created_time (Optional[datetime]): The creation time of the challenge.
        category (Optional[int]): The category of the challenge.
        cover_location (Optional[str]): The location of the challenge cover.
        days_left (Optional[int]): The days left for the challenge.
        is_group_challenge (bool): Whether the challenge is a group challenge.
    """
    title: str
    description: str
    duration: Optional[int] = None
    breaking_days: Optional[int] = None
    is_public: bool = False
    is_completed: Optional[bool] = False
    is_completed: Optional[bool] = False
    created_time: Optional[datetime] = None
    category: Optional[int] = None
    cover_location: Optional[str] = None
    days_left: Optional[int] = None
    is_group_challenge: bool


class ChallengeCreate(BaseModel):
    """
    Schema for creating a challenge.

    Attributes:
        title (str): The title of the challenge.
        description (str): The description of the challenge.
        duration (Optional[int]): The duration of the challenge.
        breaking_days (Optional[int]): The breaking days of the challenge.
        is_public (bool): Whether the challenge is public. Defaults to False.
        category (Optional[int]): The category of the challenge.
        cover_location (Optional[str]): The location of the challenge cover.
        challenge_owner_id (int): The unique identifier of the challenge owner.
    """
    title: str
    description: str
    duration: Optional[int] = None
    breaking_days: Optional[int] = None
    is_public: bool = False
    category: Optional[int] = None
    cover_location: Optional[str] = None

    challenge_owner_id: int


class ChallengeRead(ChallengeBase):
    """
    Schema for reading a challenge.

    Attributes:
        id (int): The unique identifier of the challenge.
        title (str): The title of the challenge.
        description (str): The description of the challenge.
        duration (int): The duration of the challenge.
        breaking_days (int): The breaking days of the challenge.
        is_public (bool): Whether the challenge is public.
        category (int): The category of the challenge.
        created_time (datetime): The creation time of the challenge.
        finished_time (Optional[datetime]): The finished time of the challenge.
        cover_location (str): The location of the challenge cover.
        is_completed (bool): Whether the challenge is completed.
        challenge_owner_id (int): The unique identifier of the challenge owner.
        course_id (Optional[int]): The unique identifier of the course.
    """
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


class GroupChallengeMembersBase(BaseModel):
    """
    Schema for group challenge members data.

    Attributes:
        challenge_id (int): The unique identifier of the challenge.
        user_id (int): The unique identifier of the user.
        days_left (Optional[int]): The days left for the challenge.
        breaking_days_left (int): The breaking days left for the challenge.
        is_challenge_finished (bool): Whether the challenge is finished. 
    """
    challenge_id: int
    user_id: int
    days_left: Optional[int] = None
    breaking_days_left: int
    is_challenge_finished: bool


class GroupChallengeMembersCreate(GroupChallengeMembersBase):
    """ Schema for creating group challenge members data. 

    Attributes:
        challenge_id (int): The unique identifier of the challenge.
        user_id (int): The unique identifier of the user.
        days_left (Optional[int]): The days left for the challenge.
        breaking_days_left (int): The breaking days left for the challenge.
        is_challenge_finished (bool): Whether the challenge is finished.    
    """
    breaking_days_left: int
    days_left: Optional[int] = None
    is_challenge_finished: bool


class GroupChallengeMembersRead(GroupChallengeMembersBase):
    """ Schema for reading group challenge members data.

    Attributes:
        challenge_id (int): The unique identifier of the challenge.
        user_id (int): The unique identifier of the user.
        days_left (int): The days left for the challenge.
        breaking_days_left (int): The breaking days left for the challenge.
        is_challenge_finished (bool): Whether the challenge is finished.
    """
    breaking_days_left: int
    days_left: Optional[int] = None
    is_challenge_finished: bool

    class Config:
        orm_mode = True


class ChallengeWithBreakingDays(ChallengeRead):
    """ Schema for challenge with breaking days data.
    Assuming ChallengeRead is your base schema for reading challenges

    Attributes:
        id (int): The unique identifier of the challenge.
        title (str): The title of the challenge.
        description (str): The description of the challenge.
        duration (int): The duration of the challenge.
        breaking_days (int): The number of breaking days allowed in the challenge.
        is_public (bool): Whether the challenge is public.
        category (int): The category ID of the challenge.
        created_time (datetime): The creation time of the challenge.
        finished_time (Optional[datetime]): The finish time of the challenge.
        cover_location (str): The location of the challenge cover.
        challenge_owner_id (int): The ID of the challenge owner.
        course_id (Optional[int]): The course ID associated with the challenge.
        is_completed (bool): Whether the challenge is completed.
        days_left (int): The number of days left for the challenge.
        is_group_challenge (bool): Whether the challenge is a group challenge.
        breaking_days_left (int): The number of breaking days left for the challenge.
    """
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


class PostBase(BaseModel):
    """ Schema for post base data.

    Attributes:
        created_time (Optional[datetime]): The creation time of the post.
        start_time (datetime): The start time of the post.
        end_time (datetime): The end time of the post.
        written_text (str): The written text of the post.
    """
    created_time: Optional[datetime] = None
    start_time: datetime
    end_time: datetime
    written_text: str


class PostCreate(BaseModel):
    """ Schema for creating post data.

    when creating a post, the image_location is optional, because the user may not upload an image
    create post will create a post and a post_content at the same time
    if user wants to upload an image, the image_location will be updated in the post_content table

    Attributes:
        user_id (int): The unique identifier of the user.
        challenge_id (int): The unique identifier of the challenge.
        start_time (datetime): The start time of the post.
        end_time (datetime): The end time of the post.
        written_text (str): The written text of the post.
        image_location (Optional[str]): The location of the image. Defaults
    """
    user_id: int
    challenge_id: int
    start_time: datetime
    end_time: datetime
    written_text: str
    image_location: Optional[str] = None


class PostRead(PostBase):
    """ Schema for reading post data.

    Attributes:
        id (int): The unique identifier of the post.
        user_id (int): The unique identifier of the user.
        challenge_id (int): The unique identifier of the challenge.
        start_time (datetime): The start time of the post.
        end_time (datetime): The end time of the post.
        written_text (str): The written text of the post.
        image_location (Optional[str]): The location of the image.
    """
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


class TrackingsRequest(BaseModel):
    """ Schema for tracking request data.

    Attributes:
        created_time (Optional[datetime]): The creation time of the tracking.
        terminated_time (Optional[datetime]): The termination time of the tracking.
        is_terminated (Optional[bool]): Whether the tracking is terminated.
        owner_id (int): The unique identifier of the owner.
        follower_id (int): The unique identifier of the follower.
        challenge_id (int): The unique identifier of the challenge.
    """
    created_time: Optional[datetime] = None
    terminated_time: Optional[datetime] = None
    is_terminated: Optional[bool] = False
    owner_id: int
    follower_id: int
    challenge_id: int


class TrackingsResponse(BaseModel):
    """ Schema for tracking response data.

    Attributes:
        id (int): The unique identifier of the tracking.
        created_time (datetime): The creation time of the tracking.
        terminated_time (Optional[datetime]): The termination time of the tracking.
        is_terminated (bool): Whether the tracking is terminated.
        owner_id (int): The unique identifier of the owner.
        follower_id (int): The unique identifier of the follower.
        challenge_id (int): The unique identifier of the challenge.
    """
    id: int
    created_time: datetime
    terminated_time: Optional[datetime] = None
    is_terminated: bool
    owner_id: int
    follower_id: int
    challenge_id: int

    class Config:
        orm_mode = True


class PostContentBase(BaseModel):
    """ Schema for post content base data.

    Attributes:
        video_location (Optional[str]): The location of the video.
        image_location (Optional[str]): The location of the image.
        voice_location (Optional[str]): The location of the voice.
    """
    video_location: Optional[str]
    image_location: Optional[str]
    voice_location: Optional[str]


class PostContentCreate(PostContentBase):
    """ Schema for creating post content data.

    Attributes:
        post_id (int): The unique identifier of the post.
        video_location (Optional[str]): The location of the video.
        image_location (Optional[str]): The location of the image.
        voice_location (Optional[str]): The location
    """
    post_id: int


class PostContentRead(PostContentBase):
    """ Schema for reading post content data.

    Attributes:
        id (int): The unique identifier of the post content.
        post_id (int): The unique identifier of the post.
        video_location (Optional[str]): The location of the video.
        image_location (Optional[str]): The location of the image.
        voice_location (Optional[str]): The location of the voice.
    """
    id: int
    post_id: int

    class Config:
        orm_mode = True


class CourseResponse(BaseModel):
    """ Schema for course response data.

    Attributes:
        id (int): The unique identifier of the course.
        course_name (str): The name of the course.
        category (int): The category of the course.
        description (str): The description of the course.
        cover_location (Optional[str]): The location of the course cover.
        source_link (str): The source link of the course.
        short_intro (str): The short introduction of the course.
    """
    id: int
    course_name: str
    category: int
    description: str
    cover_location: Optional[str] = None
    source_link: str
    short_intro: str

    class Config:
        orm_mode = True


class UserReactionLogBase(BaseModel):
    """ Schema for user reaction log base data.

    Attributes:
        created_datetime (datetime): The creation time of the log.
        is_cancelled (bool): Whether the log is cancelled
    """
    created_datetime: datetime
    is_cancelled: bool


class UserReactionLogCreate(UserReactionLogBase):
    """ Schema for creating user reaction log data.

    Attributes:
        user_id (int): The unique identifier of the user.
        post_id (int): The unique identifier of the post.
        emoji_image (str): The location of the emoji image.
    """
    user_id: int
    post_id: int
    emoji_image: str


class UserReactionLogRead(UserReactionLogBase):
    """ Schema for reading user reaction log data.

    Attributes:
        log_id (int): The unique identifier of the log.
        user_id (int): The unique identifier of the user.
        post_id (int): The unique identifier of the post.
        emoji_image (str): The location of the emoji image.
    """
    log_id: int
    user_id: int
    post_id: int
    emoji_image: str

    class Config:
        orm_mode = True


class EmojiBase(BaseModel):
    """ Schema for emoji base data.

    Attributes:
        name (str): The name of the emoji.
    """
    name: str


class PostReactionBase(BaseModel):
    """ Schema for post reaction base data.

    Attributes:
        post_id (int): The unique identifier of the post.
    """
    count: int


class PostReactionCreate(PostReactionBase):
    """ Schema for creating post reaction data.

    Attributes:
        post_id (int): The unique identifier of the post.
        emoji_image (str): The location of the emoji image.
        count (int): The count of the post reaction.
    """
    post_id: int
    emoji_image: str

    class Config:
        orm_mode = True


class ChallengesDiscover(BaseModel):
    """ Schema for discover challenge data.
    Attributes:
        id (int): The unique identifier of the challenge.
        cover_location (str): The location of the challenge cover.
        title (str): The title of the challenge.
        owner_id (int): The unique identifier of the challenge owner.
        owner_avatar (str): The location of the challenge owner's avatar.
        follower_avatars (list): The locations of the follower avatars.
        challenge_process (float): The process of the challenge.
    """
    id: int
    cover_location: str
    title: str
    owner_id: int
    owner_avatar: str
    follower_avatars: list
    challenge_process: float

    class Config:
        orm_mode = True


class GroupChallengesMember(BaseModel):
    """ Schema for group challenge member data.
    Attributes:
        user_id (int): The unique identifier of the user.
        breaking_days_left (int): The breaking days left for the challenge.
        days_left (int): The days left for the challenge.
        is_challenge_finished (bool): Whether the challenge is finished.
        challenge_id (int): The unique identifier of the challenge.
        user_name (str): The name of the user.
        challenge_category (int): The category of the challenge.
    """
    user_id: int
    breaking_days_left: int
    days_left: int
    is_challenge_finished: bool
    challenge_id: int
    user_name: str
    challenge_category: int

    class Config:
        orm_mode = True


class ExpoPushTokenBase(BaseModel):
    """ Schema for expo push token data.

    Attributes:
        expo_push_token (str): The expo push token.
        user_id (int): The unique identifier of the user.
        timestamp (datetime): The timestamp of the expo push token.
    """
    expo_push_token: str
    user_id: int
    timestamp: datetime


class BlockUserListBase(BaseModel):
    """ Schema for block user list data.

    Attributes:
        blocker_user_id (int): The unique identifier of the blocker user.
        blocked_user_id (int): The unique identifier of the blocked user.
    """
    blocker_user_id: int
    blocked_user_id: int
