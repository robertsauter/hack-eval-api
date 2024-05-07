import os
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv('SECRET_KEY')
DB_CONNECTION = os.getenv('DB_CONNECTION')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='hackpulseanalyzer/users/login')
