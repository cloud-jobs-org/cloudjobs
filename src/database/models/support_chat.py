import uuid
from datetime import datetime
from pydantic import BaseModel, Field, Extra

import random


def create_colour():
    # Generate a random color code in hexadecimal format
    color_code = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    return color_code


def timestamp() -> str:
    return str(datetime.utcnow())


def create_id() -> str:
    return str(uuid.uuid4())


class ChatUser(BaseModel):
    uid: str
    display_name: str
    user_banned: bool = Field(default=False)
    colour: str = Field(default_factory=create_colour)


class ChatMessage(BaseModel):
    uid: str
    message_id: str = Field(default_factory=create_id)
    text: str
    timestamp: str = Field(default_factory=timestamp)
    user_colour: str | None