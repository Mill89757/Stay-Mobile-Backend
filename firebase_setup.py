import os
import json
import base64

from firebase_admin import credentials,  initialize_app
from dotenv import load_dotenv


# load env file
load_dotenv(override=True)
ENCODED_KEY = os.getenv("ENCODED_FIREBASE_KEY")[2:-1]


# decode
original_firebase_key = json.loads(
    base64.b64decode(ENCODED_KEY).decode('utf-8'))

cred = credentials.Certificate(original_firebase_key)
firebase_app = initialize_app(cred)
