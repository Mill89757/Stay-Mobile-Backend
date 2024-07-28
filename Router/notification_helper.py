import re

import requests
from exponent_server_sdk import (DeviceNotRegisteredError, PushClient,
                                 PushMessage, PushServerError, PushTicketError)
from fastapi import APIRouter
from requests.exceptions import ConnectionError, HTTPError
from sqlalchemy.orm import Session

import CRUD.challenge as crud_challenge
import CRUD.expo_push_token as crud_token

session = requests.Session()

router = APIRouter()

session.headers.update(
    {
        # "Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)


def get_push_tokens(db: Session):
    """ Get expo push tokens for user who do not complete daily post """
    user_id_list = crud_challenge.check_user_activity(db=db)
    tokens = set()
    for user_id in user_id_list:
        token = crud_token.get_expo_push_token(db=db, user_id=user_id)
        if token is not None:
            tokens.add(token.expo_push_token)
    return tokens


def push_message_array(tokens):
    """ Build PushMessage array to store push notification chunks """
    push_messages = []
    for token in tokens:
        push_message = PushMessage(
            to=token,
            title="Reminder: Create A Post Now!",
            body="Let\'s stay on your challenge, keep going and post it on Stay!"
        )
        push_messages.append(push_message)
    return push_messages


def send_push_notification(push_messages, db: Session):
    """ Send push notification to users who have not complete daily challenge """
    try:
        push_tickets = PushClient(session=session).publish_multiple(
            push_messages=push_messages)
    except PushServerError:  # Check if there's any error when sending message to Expo server
        raise ConnectionError('Invalid server response')
    except (ConnectionError, HTTPError) as exc:
        raise PushServerError('Invalid server response')

    for t in push_tickets:
        try:
            t.validate_response()
        except DeviceNotRegisteredError:
            invalid_token = t.push_message.to       # delete inactive tokens
            crud_token.delete_token_by_token(db=db, token=invalid_token)
        except PushTicketError as exc:
            raise exc.push_response

    return push_tickets


def validate_receipts(push_tickets, db: Session):
    """     
        Wait for 30 mins to fetch and validate receipts
        Validate push notification receipts 
    """

    def get_token_from_message(message):
        """ Extract Expo token from error message """
        token = re.search("ExponentPushToken\[\w+\]", message)
        return token

    push_client = PushClient(session=session)
    receipts = push_client.check_receipts_multiple(push_tickets=push_tickets)
    for r in receipts:
        try:
            r.validate_response()
        except DeviceNotRegisteredError as exc:
            token = get_token_from_message(r.message)
            crud_token.delete_token_by_token(db=db, token=token)
            raise exc.push_response
    return
