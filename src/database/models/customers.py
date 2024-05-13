from pydantic import BaseModel, Field

from src.utils import string_today, create_customer_id


class Employee:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.permissions = set()

    def add_permission(self, permission):
        self.permissions.add(permission)

    def has_permission(self, permission):
        return permission in self.permissions


class CustomerDetails(BaseModel):
    """
    Customer Details
    """

    customer_id: str
    uid: str

    full_names: str
    surname: str

    email: str
    contact_number: str

    date_joined: str = Field(default_factory=string_today)
    is_active: bool = Field(default=True)
    delivery_address_id: str | None
    address_id: str | None
    contact_id: str | None
    postal_id: str | None
    bank_account_id: str | None
