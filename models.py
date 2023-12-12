from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

# create User class inherited from Base class 
class User(Base):
    # name of the table used in database
    __tablename__ = "User"

    # create attributes
    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, nullable=False)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email_address = Column(String)
    # created_time = Column(DateTime)
    created_time = Column(DateTime, default = func.now(), nullable=False)
    avatar_location = Column(String)
    is_completed = Column(Boolean, default=False)#默认 false

# create Tracking class inherited from Base class
class Tracking(Base):
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True, index=True)
    created_time = Column(DateTime)
    terminated_time = Column(DateTime)
    is_terminated = Column(Boolean)
    owner_id = Column(ForeignKey("User.id"), nullable=False)
    follower_id = Column(ForeignKey("User.id"), nullable=False)
    challenge_id = Column(ForeignKey('challenge.id'), nullable=False)

# create Challeng class inherited from Base class
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
    user_id = Column(ForeignKey("User.id"), nullable=False)
    course_id = Column(ForeignKey("course.id"), nullable=True)
    is_finished = Column(Boolean, default= False ,nullable=False)
    days_left = Column(Integer)
    breaking_days_left = Column(Integer)

# create Post class inherited from Base class
class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("User.id"), nullable=False)
    challenge_id = Column(ForeignKey("challenge.id"), nullable=False)
    created_time = Column(DateTime, default = func.now(), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    written_text = Column(String(1000))

# create PostContent class inherited from Base class
class PostContent(Base):
    __tablename__ = "post_content"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(ForeignKey("post.id"), nullable=False)
    video_location = Column(String)
    image_location = Column(String)
    voice_location = Column(String)

# create Reaction class inherited from Base class
class Reaction(Base):
    __tablename__ = "reaction"

    id = Column(Integer, primary_key=True, index=True)
    emoji_type = Column(Integer)
    amount = Column(Integer)
    post_id = Column(ForeignKey("post.id"), nullable=False)
    user_id = Column(ForeignKey("User.id"), nullable=False)

# create Course class inherited from Base class
class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable= False)
    category = Column(Integer, nullable= False)
    description = Column(String, nullable=False)
    cover_location = Column(String, nullable=False)

# craete User_reaction_log class inherited from Base class
class User_reaction_log(Base):
    __tablename__ = "user_reaction_log"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("User.id"), nullable=False)
    post_id = Column(ForeignKey("post_id"), nullable=False)
    emoji_id = Column(ForeignKey("emoji_id"), nullable=False)
    created_datetime = Column(datetime,nullable=False)
    is_cancelled = Column(bool, nullable=False)