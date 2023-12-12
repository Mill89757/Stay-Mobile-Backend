from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas
from database import get_db
import CRUD.user_reaction_log as crud
from typing import List

# create routes fro challenges operations and functions
router = APIRouter()

# create user reaction log 

# read all user reaction log

# read user reaction log by log id

# read user reaction log by user id

# read user reaction log by post id

# read user reaction log by emoji id

# read the most recent user reaction log by user id and post id