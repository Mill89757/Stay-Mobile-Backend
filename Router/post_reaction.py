from re import S
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas
from database import get_db
import CRUD.post_reaction as crud
import CRUD.post as crud_post
from typing import List

# create routes for post reaction operations and functions
router = APIRouter(prefix="/post_reaction")

# create post reaction log
@router.post("/Create", response_model=schemas.PostReactionCreate, status_code=status.HTTP_201_CREATED)
async def create_post_reaction(post_reaction:schemas.PostReactionCreate, db:Session=Depends(get_db)):
    return crud.creat_post_reaction(db=db, post_reaction=post_reaction)

# read all post reaction
@router.get("", response_model=List[schemas.PostReactionCreate])
async def get_all_reactions(skip:int = 0, limit:int = 100, db:Session=Depends(get_db)):
    all_post_reaction = crud.get_post_reactions(db=db, skip=skip, limit=limit)
    return all_post_reaction

# read post reactions by post id
@router.get("/GetByPostId/{post_id}", response_model=List[schemas.PostReactionCreate])
async def get_reactions_by_post_id(post_id:int, db:Session=Depends(get_db)):
    reactions_post_id = crud.get_post_reactions_by_postid(db=db, post_id=post_id)
    return reactions_post_id

# read post reactions by emoji image
@router.get("/GetByEmoji/{emoji_image}", response_model=List[schemas.PostReactionCreate])
async def get_reactions_by_emoji(emoji_image:str, db:Session=Depends(get_db)):
    reactions_emoji = crud.get_post_reactions_by_emoji_image(db=db, emoji_image=emoji_image)
    return reactions_emoji

# read post reaction by post id and emoji image
@router.get("/GetByPostnEmoji/{post_id}/{emoji_image}", response_model=schemas.PostReactionCreate)
async def get_reaction_by_postid_emoji(post_id:int, emoji_image:str, db:Session=Depends(get_db)):
    reaction_post_emoji = crud.get_post_reaction_by_post_emoji(db=db, post_id=post_id, emoji_image=emoji_image)
    return reaction_post_emoji

# update post reaction by post id and emoji image
@router.put("/UpdateReaction/{post_id}/{emoji_image}", response_model=schemas.PostReactionCreate)
async def update_post_reaction(post_id:int, emoji_image:str, db:Session=Depends(get_db)):
    updated_reaction= crud.update_post_reaction(db=db, post_id=post_id, emoji_image=emoji_image)
    return updated_reaction

# delete post reaction by post id and emoji image
@router.delete("/DeleteReaction/{post_id}/{emoji_image}", status_code=status.HTTP_204_NO_CONTENT)
async def delet_reaction(post_id:int, emoji_image:str, db:Session=Depends(get_db)):
    if not crud.delete_post_reaction(post_id=post_id, emoji_image=emoji_image, db=db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reaction not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail":"Reaction deleted successfully"})

# update count by post id and emoji image
# action: True: hit the button; False: cancel reaction
@router.put("/UpdateCount/{post_id}/{emoji_image}", response_model=schemas.PostReactionCreate)
async def update_count(post_id:int, emoji_image:str, action:bool, db:Session=Depends(get_db)):
    updated_reaction = crud.update_count(db=db, post_id=post_id, emoji_image=emoji_image, action=action)
    return updated_reaction

# read reaction count by challenge id
@router.get("/GetReactionsByChallenge/{challenge_id}")
async def get_reaction_count_challenge_id(challenge_id:int, db:Session=Depends(get_db)):
    post_list = crud_post.get_posts_by_challenge_id(db=db, challenge_id=challenge_id)
    challenge_reaction_count = 0
    post_id_List = []
    for item in post_list:
        post_id_List.append(item.id)
    for id in post_id_List:
        challenge_reaction_count += crud.get_counts_post(db=db, post_id=id)
    return challenge_reaction_count
