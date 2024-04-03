from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials,  initialize_app
import os
from dotenv import load_dotenv
import json
# load env file
load_dotenv()

# # firebase_credentials = json.dumps({
# #     "type": os.environ["FIREBASE_TYPE"],
# #     "project_id": os.environ["FIREBASE_PROJECT_ID"],
# #     "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
# #     # "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace('\\n', '\n'),
# #     "private_key": os.environ["FIREBASE_PRIVATE_KEY"],
# #     "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
# #     "client_id": os.environ["FIREBASE_CLIENT_ID"],
# #     "auth_uri": os.environ["FIREBASE_AUTH_URI"],
# #     "token_uri": os.environ["FIREBASE_TOKEN_URI"],
# #     "auth_provider_x509_cert_url": os.environ["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"],
# #     "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
# #     "universe_domain":  os.environ["FIREBASE_DOMAIN"]
# # })

# firebase_credential = json.loads(os.getenv('FIREBASE_JSON'))

cred = credentials.Certificate('./stay-mobile-b2c29-firebase-adminsdk-rg9km-1de89e262d.json')

# # # 初始化Firebase Admin SDK
# cred = credentials.Certificate(firebase_credential)
# # print("++++++++++++++++++++++++++++++++++++++++++++++++")
# # print(type(firebase_credentials))
# # # print(type(cred))
# # print("+++++++++++++++++++++++++++++++++++++++++++++++++")
# firebase_app = initialize_app(cred)

# # firebase_credentials = json.dumps(cred)
# print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
# # print(type(firebase_credentials))

# firebase_credentials = json.loads(os.environ["FIREBASE_JSON"])
# cred = credentials.Certificate(firebase_credentials)
firebase_app = initialize_app(cred)