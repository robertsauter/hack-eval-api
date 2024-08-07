'''Routes for handling user authentication'''

from fastapi import APIRouter, Depends, Form
from src.models.User import UserInDB, User
from src.models.Token import Token
from typing import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.collection import Collection
from src.lib.database import users_collection
from src.lib.http_exceptions import HTTP_401, HTTP_409
from datetime import timedelta, datetime
from jose import jwt
from src.lib.globals import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, OAUTH2_SCHEME
from bson.objectid import ObjectId

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

router = APIRouter()


def create_access_token(user_id: str) -> str:
    '''Creates an access token, that can be sent to verify, that a user is logged in'''
    access_token_expires = datetime.utcnow(
    ) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {'sub': user_id, 'exp': access_token_expires}
    return jwt.encode(data, SECRET_KEY, ALGORITHM)


def authenticate_user(
        username: str,
        password: str,
        users: Collection
) -> UserInDB | None:
    '''Checks if username and password are correct and returns user object if yes'''
    user: dict | None = users.find_one({'username': username})
    if user is None:
        return None
    if not password_context.verify(password, user['hashed_password']):
        return None
    user_in_db = UserInDB(
        id=str(user['_id']),
        username=user['username'],
        hashed_password=user['hashed_password']
    )
    return user_in_db


@router.post('')
def register(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    users: Annotated[Collection, Depends(users_collection)]
) -> str:
    '''Register a new user'''
    # Check if the username is already taken
    if users.find_one({'username': form_data.username}) is not None:
        HTTP_409('Username already exists')
    # Insert a new user into the database
    users.insert_one({
        'username': form_data.username,
        'hashed_password': password_context.hash(form_data.password)
    })
    return 'Successfully registered'


@router.post('/login', response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    users: Annotated[Collection, Depends(users_collection)]
) -> Token:
    '''Login an existing user'''
    user = authenticate_user(form_data.username, form_data.password, users)
    if user is None:
        HTTP_401('Username or password not found')
    access_token: str = create_access_token(user.id)
    return Token(access_token=access_token, token_type='bearer')


@router.post('/password')
def update_password(
    old_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    users: Annotated[Collection, Depends(users_collection)]
):
    '''Update the password of a user'''
    user_id = ObjectId(jwt.decode(token, SECRET_KEY,
                       algorithms=[ALGORITHM])['sub'])
    user = users.find_one({'_id': user_id})
    password_correct = password_context.verify(
        old_password, user['hashed_password'])
    if user is None or not password_correct:
        HTTP_401('Password incorrect')
    users.update_one(
        {
            '_id': user_id
        },
        {
            '$set': {'hashed_password': password_context.hash(new_password)}
        }
    )
    return 'Success'


@router.post('/username')
def update_username(
    username: Annotated[str, Form()],
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    users: Annotated[Collection, Depends(users_collection)]
):
    '''Update the username of a user'''
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    if users.find_one({'username': username}) is not None:
        HTTP_409('Username already taken')
    users.update_one(
        {
            '_id': ObjectId(user_id)
        },
        {
            '$set': {'username': username}
        }
    )
    return 'Success'


@router.get('/current')
def get_logged_in_user(
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    users: Annotated[Collection, Depends(users_collection)]
) -> User:
    '''Get the currently logged in user'''
    user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['sub']
    user = users.find_one({'_id': ObjectId(user_id)})
    return User.model_validate(user)
