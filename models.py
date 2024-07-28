# pylint: disable=too-few-public-methods
# pylint: disable=not-callable

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import func

from database import Base


class User(Base):
    """ User table """
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, nullable=False)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email_address = Column(String)
    created_time = Column(DateTime, default=func.now(), nullable=False)
    avatar_location = Column(String)
    is_completed = Column(Boolean, default=False)
    user_timezone = Column(String, nullable=False)
    is_blocked = Column(Boolean, nullable=False, default=False)


class Tracking(Base):
    """ Tracking table """
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True, index=True)
    created_time = Column(DateTime)
    terminated_time = Column(DateTime)
    is_terminated = Column(Boolean)
    owner_id = Column(ForeignKey("User.id"), nullable=False)
    follower_id = Column(ForeignKey("User.id"), nullable=False)
    challenge_id = Column(ForeignKey('challenge.id'), nullable=False)


class Challenge(Base):
    """ Challenge table """
    __tablename__ = "challenge"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    duration = Column(Integer)
    breaking_days = Column(Integer)
    is_public = Column(Boolean, default=False)
    category = Column(String)
    created_time = Column(DateTime, default=func.now(), nullable=False)
    finished_time = Column(DateTime, nullable=True)
    cover_location = Column(String)
    challenge_owner_id = Column(ForeignKey("User.id"), nullable=False)
    course_id = Column(ForeignKey("course.id"), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=True)
    is_group_challenge = Column(Boolean, default=False, nullable=True)


class GroupChallengeMembers(Base):
    """ Group Challenge Members table """
    __tablename__ = "groupchallengemembers"

    challenge_id = Column(Integer, ForeignKey(
        'challenge.id'), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('User.id'),
                     primary_key=True, index=True)
    breaking_days_left = Column(Integer, nullable=False)
    is_challenge_finished = Column(Boolean, default=False, nullable=False)
    days_left = Column(Integer, nullable=False)


class Post(Base):
    """ Post table """
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("User.id"), nullable=False)
    challenge_id = Column(ForeignKey("challenge.id"), nullable=False)
    created_time = Column(DateTime, default=func.now(), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    written_text = Column(String(1000))


class PostContent(Base):
    """ Post Content table """
    __tablename__ = "post_content"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(ForeignKey("post.id"), nullable=False)
    video_location = Column(String)
    image_location = Column(String)
    voice_location = Column(String)


class Reaction(Base):
    """ Reaction table """
    __tablename__ = "reaction"

    id = Column(Integer, primary_key=True, index=True)
    emoji_type = Column(Integer)
    amount = Column(Integer)
    post_id = Column(ForeignKey("post.id"), nullable=False)
    user_id = Column(ForeignKey("User.id"), nullable=False)


class Course(Base):
    """ Course table """
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    category = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    cover_location = Column(String, nullable=True)
    source_link = Column(String, nullable=False)
    short_intro = Column(String, nullable=False)


class UserReactionLog(Base):
    """ User Reaction Log table """
    __tablename__ = "user_reaction_log"

    log_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(ForeignKey("post.id"), nullable=False)
    user_id = Column(ForeignKey("User.id"), nullable=False)
    emoji_image = Column(ForeignKey("emoji.emoji_image"), nullable=False)
    created_datetime = Column(DateTime, default=func.now(), nullable=False)
    is_cancelled = Column(Boolean, default=False, nullable=False)


class Emoji(Base):
    """ Emoji table """
    __tablename__ = "emoji"

    emoji_image = Column(String, primary_key=True, index=False)
    name = Column(String)


class PostReaction(Base):
    """ Post Reaction table """
    __tablename__ = "post_reaction"

    post_id = Column(ForeignKey("post.id"), primary_key=True, index=True)
    emoji_image = Column(ForeignKey("emoji.emoji_image"),
                         primary_key=True, index=True)
    count = Column(Integer, nullable=False)


class ExpoPushToken(Base):
    """ Expo Push Token table """
    __tablename__ = "expo_push_token"

    expo_push_token = Column(String, primary_key=True, index=False)
    user_id = Column(ForeignKey("User.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)


class BlockedUserList(Base):
    """ Blocked User List table """
    __tablename__ = "blocked_user_list"

    blocker_user_id = Column(Integer, primary_key=True)
    blocked_user_id = Column(Integer, primary_key=True)
