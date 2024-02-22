from lib2to3.pgen2 import token
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import schemas
from database import get_db
import CRUD.expo_push_token as crud


# create routes for user reaction log operations and functions
router = APIRouter(prefix="/expo_token")

# create expo push token info
@router.post("/create", response_model=schemas.ExpoPushTokenBase,  status_code=status.HTTP_201_CREATED)
async def create_expo_token(token:schemas.ExpoPushTokenBase, db:Session=Depends(get_db)):
    token = crud.create_expo_push_token(db=db, expo_push_token=token)
    return token

# get token via user id
@router.get("/{user_id}", response_model=schemas.ExpoPushTokenBase)
async def get_token_by_user_id(user_id: int, db:Session=Depends(get_db)):
    token = crud.get_expo_push_token(db=db, user_id=user_id)
    return token

# udpate to latest version
@router.put("/updateToken/{token}", response_model=schemas.ExpoPushTokenBase)
async def update_expo_push_token(token:str, tokenInfo:schemas.ExpoPushTokenBase, db:Session=Depends(get_db)):
    updated_token = crud.update_expo_push_token(db=db, token=token, tokenInfo=tokenInfo)
    return updated_token

# delete token when not needed
@router.delete("/deleteTokenByUserId/{token}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_token(token:str, db:Session=Depends(get_db)):
    if not crud.delete_token_by_token(db=db, token=token):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expo Push Token not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail":"Expo Push Token deleted successful"})

# delete token by user id
@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_token_user_id(user_id: int, db:Session= Depends(get_db)):
    if not crud.delete_token_uid(db=db, uid=user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expo Push Token not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail":"Expo Push Token deleted successful"})