from pydantic import BaseModel

class User(BaseModel):
    username: str

class UserInDB(User):
    id: str
    hashed_password: str