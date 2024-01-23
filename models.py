from ast import For
from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, nullable=False)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email_address = Column(String)
    created_time = Column(DateTime, default = func.now(), nullable=False)
    avatar_location = Column(String)
    is_completed = Column(Boolean, default=False)
    user_timezone = Column(String, nullable=False)

class Tracking(Base):
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True, index=True)
    created_time = Column(DateTime)
    terminated_time = Column(DateTime)
    is_terminated = Column(Boolean)
    owner_id = Column(ForeignKey("User.id"), nullable=False)
    follower_id = Column(ForeignKey("User.id"), nullable=False)
    challenge_id = Column(ForeignKey('challenge.id'), nullable=False)

class Challenge(Base):
    __tablename__ = "challenge"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    duration = Column(Integer)
    breaking_days =  Column(Integer)
    is_public = Column(Boolean, default=False)
    category = Column(String)
    created_time = Column(DateTime, default = func.now(), nullable=False)
    finished_time = Column(DateTime, nullable=True)
    cover_location = Column(String)
    challenge_owner_id = Column(ForeignKey("User.id"), nullable=False)
    course_id = Column(ForeignKey("course.id"), nullable=True)
    is_finished = Column(Boolean, default= False ,nullable=False)
    days_left = Column(Integer)
    is_group_challenge = Column(Boolean, default=False, nullable=False)

class GroupChallengeMembers(Base):
    __tablename__ = "groupchallengemembers"
    challenge_id = Column(Integer, ForeignKey('challenge.id'), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True, index=True)
    breaking_days_left = Column(Integer,nullable=False)


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("User.id"), nullable=False)
    challenge_id = Column(ForeignKey("challenge.id"), nullable=False)
    created_time = Column(DateTime, default = func.now(), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    written_text = Column(String(1000))

class PostContent(Base):
    __tablename__ = "post_content"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(ForeignKey("post.id"), nullable=False)
    video_location = Column(String)
    image_location = Column(String)
    voice_location = Column(String)

class Reaction(Base):
    __tablename__ = "reaction"

    id = Column(Integer, primary_key=True, index=True)
    emoji_type = Column(Integer)
    amount = Column(Integer)
    post_id = Column(ForeignKey("post.id"), nullable=False)
    user_id = Column(ForeignKey("User.id"), nullable=False)

class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable= False)
    category = Column(Integer, nullable= False)
    description = Column(String, nullable=False)
    cover_location = Column(String, nullable=False)
    source_link = Column(String, nullable=False)
    short_intro = Column(String, nullable=False)

# craete User_reaction_log class inherited from Base class
class UserReactionLog(Base):
    __tablename__ = "user_reaction_log"

    log_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(ForeignKey("post.id"), nullable=False)
    user_id = Column(ForeignKey("User.id"), nullable=False)
    emoji_image = Column(ForeignKey("emoji.emoji_image"), nullable=False)
    created_datetime = Column(DateTime, default = func.now(), nullable=False)
    is_cancelled = Column(Boolean, default= False ,nullable=False)

# create Emoji class inherited from Base class
class Emoji(Base):
    __tablename__ = "emoji"

    emoji_image = Column(String, primary_key=True, index = False)
    name = Column(String)

# create Post Reaction class inherited from Base class
class PostReaction(Base):
    __tablename__ = "post_reaction"

    post_id = Column(ForeignKey("post.id"), primary_key=True, index=True)
    emoji_image = Column(ForeignKey("emoji.emoji_image"), primary_key=True, index=True)
    count = Column(Integer, nullable= False)

