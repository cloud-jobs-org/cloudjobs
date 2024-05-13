import uuid

from pydantic import BaseModel, Field, validator


class Auth(BaseModel):
    email: str
    username: str | None
    password: str
    remember: str | None

    @validator('username')
    def convert_to_lower(cls, value):
        return value.lower()


def generate_uuid_str():
    return str(uuid.uuid4())[:32]


class RegisterUser(BaseModel):
    uid: str = Field(default_factory=generate_uuid_str)
    username: str | None
    email: str
    password: str
    terms: str

