from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials, auth, initialize_app


# 初始化Firebase Admin SDK
cred = credentials.Certificate('./stay-mobile-b2c29-firebase-adminsdk-rg9km-1de89e262d.json')
firebase_app = initialize_app(cred)