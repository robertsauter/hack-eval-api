'''Utility functions for HTTP response codes'''

from fastapi import HTTPException, status

def HTTP_401(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={ 'WWW-Authenticate': 'Bearer' }
    )

def HTTP_403(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message
    )

def HTTP_409(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message
    )