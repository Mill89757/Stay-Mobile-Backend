from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials,  initialize_app
import os
from dotenv import load_dotenv, find_dotenv
import json
import base64
# load env file
load_dotenv(find_dotenv())
encoded_key = os.getenv("ENCODED_FIREBASE_KEY")
# remove the first two chars and the last char in the key
encoded_key = str(encoded_key)[2:-1]
# decode
original_firebase_key= json.loads(base64.b64decode(encoded_key).decode('utf-8'))
cred = credentials.Certificate(original_firebase_key)
firebase_app = initialize_app(cred)