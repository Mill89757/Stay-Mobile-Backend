import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import Router.notification_helper as helper
from database import get_db

session = requests.Session()


router = APIRouter()


@router.post("/sendNotification/")
async def test_sendNotification(db: Session = Depends(get_db)):
    """ Send a push notification to all users """
    tokens = helper.get_push_tokens(db=db)
    push_messages = helper.push_message_array(tokens=tokens)
    helper.send_push_notification(
        push_messages=push_messages, db=db)
    return {"message": "Notification sent"}
