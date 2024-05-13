import uuid
from pydantic import BaseModel, Field

from src.utils import create_id


class Address(BaseModel):
    """
    Represents an address.

    Attributes:
    - address_id (str): The unique ID of the address.
    - street (str): The street address.
    - city (str): The city.
    - state (str): The state.
    - postal_code (str): The postal code.
    - country (str): The country.
    """

    address_id: str = Field(default_factory=create_id,
                            description="The unique ID of the address.")
    address_line_1: str
    town_city: str
    province: str
    postal_code: str
    country: str


class Contacts(BaseModel):
    contact_id: str = Field(default_factory=create_id)
    cell: str
    tel: str | None
    email: str
    facebook: str | None
    twitter: str | None
    whatsapp: str | None


class PostalAddress(BaseModel):
    postal_id: str = Field(default_factory=create_id)

    address_line_1: str
    town_city: str
    province: str
    postal_code: str
    country: str

