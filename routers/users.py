'''Routes for handling user authentication'''

from fastapi import APIRouter, Depends, Request
from models.User import UserInDB
from models.Token import Token
from typing import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo.collection import Collection
from lib.database import users_collection
from lib.http_responses import HTTP_401, HTTP_403, HTTP_409
from datetime import timedelta, datetime
from jose import ExpiredSignatureError, jwt
import os

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')

router = APIRouter()

def create_access_token(username: str) -> str:
    '''Creates an access token, that can be sent to verify, that a user is logged in'''
    access_token_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = { 'sub': username, 'exp': access_token_expires }
    return jwt.encode(data, SECRET_KEY, ALGORITHM)

def authenticate_user(
        username: str,
        password: str,
        users: Collection
        ) -> UserInDB | None:
    '''Checks if username and password are correct and returns user object if yes'''
    user: dict | None = users.find_one({ 'username': username })
    if user is None:
        return None
    if not password_context.verify(password, user['hashed_password']):
        return None
    return UserInDB(**user)

@router.post('')
def register(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        users: Annotated[Collection, Depends(users_collection)]
    ):
    '''Register a new user'''
    #Check if the username is already taken
    if users.find_one({ 'username': form_data.username }) is not None:
        HTTP_409('Username already exists')
    #Insert a new user into the database
    users.insert_one({
        'username': form_data.username,
        'hashed_password': password_context.hash(form_data.password)
    })
    return { 'message': 'Successfully registered' }

@router.post('/login', response_model=Token)
def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        users: Annotated[Collection, Depends(users_collection)]
    ) -> Token:
    '''Login an existing user'''
    user: UserInDB | None = authenticate_user(form_data.username, form_data.password, users)
    if user is None:
        HTTP_401('Username or password not found')
    access_token: str = create_access_token(user.username)
    return Token(access_token=access_token, token_type='bearer')

@router.get('/test')
def test(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        HTTP_403('Token expired')
    return 'test'