from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base


class ToDo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    completed = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, nullable=False)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email_address = Column(String)
    created_time = Column(String)
    avatar_location = Column(String)
    iscompleted = Column(Boolean, default=False)

class Tracking(Base):
    __tablename__ = "trackings"

    id = Column(Integer, primary_key=True, index=True)
    created_time = Column(DateTime)
    terminated_time = Column(DateTime)
    is_terminated = Column(Boolean)
    owner_id = Column(ForeignKey("users.id"), nullable=False)
    follower_id = Column(ForeignKey("users.id"), nullable=False)
    challenge_id = Column(ForeignKey('challenges.id'), nullable=False)

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    duration = Column(Integer)
    breaking_days =  Column(Integer)
    is_public = Column(Boolean, default=False)
    # Need improvment
    category = Column(String)
    created_time = Column(DateTime)
    cover_location = Column(String)
    user_id = Column(ForeignKey("users.id"))

class ChallengesStatus(Base):
    __tablename__ = "challenge_status"

    challenge_id = Column(ForeignKey('challenges.id'), nullable=False, primary_key=True)
    is_finished = Column(Boolean)
    days_left = Column(Integer)
    breaking_days_left = Column(Integer)

class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    challenge_id = Column(ForeignKey("challenges.id"), nullable=False)
    created_time = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    #the length of content
    written_text = Column(String(1000))

class PostContent(Base):
    __tablename__ = "post_content"

    record_id = Column(ForeignKey("records.id"), nullable=False, primary_key=True)
    video_location = Column(String)
    image_location = Column(String)
    voice_location = Column(String)

class Reaction(Base):
    __tablename__ = "reaction"

    id = Column(Integer, primary_key=True, index=True)
    emoji_type = Column(Integer)
    amount = Column(Integer)
    post_id = Column(ForeignKey("post.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)

class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    # Need a FK with Challenge
    course_name = Column(String, nullable= False)
    categories = Column(Integer, nullable= False)
    description = Column(String, nullable=False)