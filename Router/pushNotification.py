from lib2to3.pgen2 import token
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError
)
import os
import requests
from requests.exceptions import ConnectionError, HTTPError
from sqlalchemy.orm import Session
from models import Challenge
session = requests.Session()
import CRUD.challenge as crud_challenge
import CRUD.expo_push_token as crud_token
import re, time
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db

router = APIRouter()

session.headers.update(
    {
        #"Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)

# get expo push tokens for user who do not complete daily post
def get_push_tokens(db:Session, challenge_id_list:list):
    user_id_list = crud_challenge.check_user_activity(db=db,challenge_id_list=challenge_id_list)
    tokens = []
    for id in user_id_list:
        token = crud_token.get_expo_push_token(db=db, user_id=id)
        if token:
            tokens.append(token)
    return tokens

# Build PushMessage array to store push noticiation chunks
def push_message_array(tokens):
    push_messages = []
    for token in tokens:
        push_message = PushMessage(
            to=token,
            title= "Reminder: Create A Post Now!",
            body= "Let\'s stay on your challenge, keep going and post it on Stay!"
        )
        push_messages.append(push_message)
    return push_messages

# Send message to users who have not complete daily challenge to Expo server and store the recipts id
def send_push_notification(push_messages, db:Session):
    try:
        push_tickets = PushClient(session=session).publish_multiple(push_messages=push_messages)
    
    # Check if there's any error when sending message to Expo server
    except PushServerError as exc:
        raise exc('Invalid server response').errors
    except (ConnectionError, HTTPError) as exc:
        raise exc.response
    
    for t in push_tickets:
        try:
            t.validate_response()
        except DeviceNotRegisteredError:
            # delete inactive tokens
            invalid_token = t.push_message.to
            crud_token.delete_token_by_token(db=db, token=invalid_token)
        except PushTicketError as exc:
            raise exc.push_response
        
    return push_tickets

# helper function to extract expo token from receipt error message
def get_Token_from_message(message):
    token = re.search("ExponentPushToken\[\w+\]", message)
    return token


# Wait for 30 mins to fetch and validate receipts
def validate_receipts(push_tickets, db: Session):
    receipts = PushClient.check_receipts_multiple(push_tickets=push_tickets)
    for r in receipts:
        try:
            r.validate_response()
        except DeviceNotRegisteredError as exc:
            token = get_Token_from_message(r.message)
            crud_token.delete_token_by_token(db=db, token=token)
            raise exc.push_response
    return 

# Send notification
def send_notification(user_id_list):
   tokens = get_push_tokens(user_id_list=user_id_list)
   push_messages = push_message_array(tokens=tokens)
   push_tickets = send_push_notification(push_messages=push_messages)

   #time.sleep(1800)
   #validate_receipts(push_tickets=push_tickets)


TIMEZONE_MAPPING = {
    "Sydney": "Australia/Sydney",
    "Perth": "Australia/Perth",
    "Brisbane": "Australia/Brisbane",
    "Beijing": "Asia/Shanghai"
}
 # router to test 
@router.post("/test/SendNotification/")
async def test_sendNotification( db: Session=Depends(get_db)):
    challenge_list = []
    #full_timezone_str = TIMEZONE_MAPPING.get(timezone, "UTC")
    tokens = get_push_tokens(db=db, challenge_id_list=challenge_list)
    push_messages = push_message_array(tokens=tokens)
    push_tickets = send_push_notification(push_messages=push_messages, db=db)
    #time.sleep(1800)
    #validate_receipts(push_tickets=push_tickets,db=db)
    
        
'''Below function only for test send notification from backend to device'''

# get expo push tokens for user who do not complete daily post
def get_push_token_test(db:Session):
    user_id_list = [10002,10009]
    tokens = []
    for id in user_id_list:
        token = crud_token.get_expo_push_token(db=db, user_id=id).expo_push_token
        if token:
            tokens.append(token)
    return tokens

# Build PushMessage array to store push noticiation chunks
def push_message_array_test(tokens):
    push_messages = []
    for token in tokens:
        push_message = PushMessage(
            to=token,
            title= "Reminder: Create A Post Now!",
            body= "Let\'s stay on your challenge, keep going and post it on Stay!"
        )
        push_messages.append(push_message)
    return push_messages

# Send message to users who have not complete daily challenge to Expo server and store the recipts id
def send_push_notification_test(push_messages, db:Session):
    try:
        push_tickets = PushClient(session=session).publish_multiple(push_messages=push_messages)
    
    # Check if there's any error when sending message to Expo server
    except PushServerError as exc:
        raise exc('Invalid server response').errors
    except (ConnectionError, HTTPError) as exc:
        raise exc.response
    
    for t in push_tickets:
        try:
            t.validate_response()
        except DeviceNotRegisteredError:
            # delete inactive tokens
            invalid_token = t.push_message.to
            crud_token.delete_token_by_token(db=db, token=invalid_token)
        except PushTicketError as exc:
            raise exc.push_response
        
    return push_tickets



# Wait for 30 mins to fetch and validate receipts
def validate_receipts_test(push_tickets, db: Session):
    receipts = PushClient.check_receipts_multiple(push_tickets=push_tickets)
    for r in receipts:
        try:
            r.validate_response()
        except DeviceNotRegisteredError as exc:
            token = get_Token_from_message(r.message)
            crud_token.delete_token_by_token(db=db, token=token)
            raise exc.push_response

# Send notification
def send_notification(user_id_list):
   tokens = get_push_tokens(user_id_list=user_id_list)
   push_messages = push_message_array(tokens=tokens)
   push_tickets = send_push_notification(push_messages=push_messages)

   time.sleep(1800)
   validate_receipts(push_tickets=push_tickets)


TIMEZONE_MAPPING = {
    "Sydney": "Australia/Sydney",
    "Perth": "Australia/Perth",
    "Brisbane": "Australia/Brisbane",
    "Beijing": "Asia/Shanghai"
}
 # router to test 
@router.post("/test/SendNotificationTest")
async def test_sendNotification_test(db: Session=Depends(get_db)):
    
    tokens = get_push_token_test(db=db)
    push_messages = push_message_array_test(tokens=tokens)
    push_tickets = send_push_notification_test(push_messages=push_messages, db=db)
    print(push_tickets)
    #time.sleep(1800)
    #validate_receipts(push_tickets=push_tickets,db=db)
    
