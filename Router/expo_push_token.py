from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import schemas
from database import get_db
import CRUD.expo_push_token as crud


router = APIRouter(prefix="/expo_token")


@router.post("/create", response_model=schemas.ExpoPushTokenBase,
             status_code=status.HTTP_201_CREATED)
async def create_expo_token(token: schemas.ExpoPushTokenBase, db: Session = Depends(get_db)):
    """ Create new expo push token """
    token = crud.create_expo_push_token(db=db, new_token=token)
    return token


@router.get("/{user_id}", response_model=schemas.ExpoPushTokenBase)
async def get_token_by_user_id(
        user_id: int, db: Session = Depends(get_db)):
    """ Get expo push token by user id """
    token = crud.get_expo_push_token(db=db, user_id=user_id)
    return token


@router.put("/updateToken/{token}", response_model=schemas.ExpoPushTokenBase)
async def update_expo_push_token(
        token: str, token_info: schemas.ExpoPushTokenBase,
        db: Session = Depends(get_db)):
    """ Update expo push token """
    updated_token = crud.update_expo_push_token(
        db=db, token=token, tokenInfo=token_info)
    return updated_token


@router.delete("/deleteTokenByUserId/{token}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_token(token: str, db: Session = Depends(get_db)):
    """ Delete expo push token """
    if not crud.delete_token_by_token(db=db, token=token):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Expo Push Token not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Expo Push Token deleted successful"})


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_token_user_id(user_id: int, db: Session = Depends(get_db)):
    """ Delete expo push token by user id """
    if not crud.delete_token_uid(db=db, uid=user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Expo Push Token not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Expo Push Token deleted successful"})
