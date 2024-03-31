from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials,  initialize_app
import os
from dotenv import load_dotenv
# load env file
load_dotenv()

firebase_credentials = {
    "type": os.environ["FIREBASE_TYPE"],
    "project_id": os.environ["FIREBASE_PROJECT_ID"],
    "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
    # "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace('\\n', '\n'),
    "private_key": os.environ["FIREBASE_PRIVATE_KEY"],
    "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
    "client_id": os.environ["FIREBASE_CLIENT_ID"],
    "auth_uri": os.environ["FIREBASE_AUTH_URI"],
    "token_uri": os.environ["FIREBASE_TOKEN_URI"],
    "auth_provider_x509_cert_url": os.environ["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"],
    "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
}


# 初始化Firebase Admin SDK
cred = credentials.Certificate(firebase_credentials)
firebase_app = initialize_app(cred)