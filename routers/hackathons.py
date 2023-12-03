'''Routes for handling hackathon objects'''

from fastapi import APIRouter, Depends
from models.RawHackathon import RawHackathon
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')

router = APIRouter()

@router.post('')
def upload_hackathon(raw_hackathon: RawHackathon) -> str:
    '''Process and save a hackathon object in the database'''
    return 'Success'