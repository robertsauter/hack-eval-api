from pydantic import BaseModel


class User(BaseModel):
    username: str
    role: str | None = None


class UserInDB(User):
    id: str
    hashed_password: str
