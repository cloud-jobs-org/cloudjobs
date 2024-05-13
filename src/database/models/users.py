import uuid
from enum import Enum

from pydantic import BaseModel, Field, Extra

from src.main import encryptor
from src.utils import create_customer_id


class UserType(str, Enum):
    ADMIN = 'admin'
    GAMER = 'gamer'


class User(BaseModel):
    """
    Represents the details of a user.

    Attributes:
    - uid (str): The ID of the user.
    - company_id (str): The ID of the company_id associated with the user.
    - is_tenant (bool): Indicates if the user is a tenant.
    - tenant_id (str): The ID of the tenant associated with the user.
    - user_type (UserType): The type of user.
    - username (str): The username of the user.
    - password (str | None): The password of the user.
    - email (str): The email address of the user.
    - full_name (str): The full name of the user.
    - contact_number (str): The contact number of the user.
    """
    uid: str
    customer_id: str = Field(default_factory=create_customer_id)
    username: str | None
    password_hash: str
    email: str

    account_verified: bool = Field(default=False)

    is_system_admin: bool = Field(default=False)
    is_company_admin: bool = Field(default=False)
    is_employee: bool = Field(default=False)
    is_client: bool = Field(default=False)

    def __bool__(self) -> bool:
        return bool(self.uid) and bool(self.username) and bool(self.password_hash)

    def is_login(self, password: str) -> bool:
        """

        :param password:
        :return:
        """
        return encryptor.compare_hashes(hash=self.password_hash, password=password)

    def __eq__(self, other):
        """
        Compare two User instances based on their uid only.

        :param other: The other User instance to compare.
        :return: True if uid of both instances is the same, False otherwise.
        """
        if not isinstance(other, User):
            return False
        return self.uid == other.uid


class CreateUser(BaseModel):
    uid: str
    username: str | None
    password: str
    email: str
    account_verified: bool = Field(default=False)

    is_system_admin: bool = Field(default=False)
    is_company_admin: bool = Field(default=False)
    is_employee: bool = Field(default=False)
    is_client: bool = Field(default=False)

    @property
    def password_hash(self):
        print(f"Password : {self.password}")
        return encryptor.create_hash(password=self.password)

    def to_dict(self) -> dict[str, str | bool]:
        dict_ = self.dict(exclude={'password'})
        dict_.update(dict(password_hash=self.password_hash))
        print(f"Update User : {dict_}")
        return dict_


class PasswordResetUser(BaseModel):
    uid: str
    username: str | None
    password: str
    email: str
    account_verified: bool = Field(default=False)

    is_system_admin: bool = Field(default=False)
    is_company_admin: bool = Field(default=False)
    is_employee: bool = Field(default=False)
    is_client: bool = Field(default=False)

    @property
    def password_hash(self):
        return encryptor.create_hash(password=self.password)

    def to_dict(self) -> dict[str, str | bool]:
        dict_ = self.dict(exclude={'password'})
        dict_.update(dict(password_hash=self.password_hash))
        print(f"Update User : {dict_}")
        return dict_


class UserUpdate(BaseModel):
    uid: str
    username: str | None
    email: str
    account_verified: bool = Field(default=False)

    is_system_admin: bool = Field(default=False)
    is_company_admin: bool = Field(default=False)
    is_employee: bool = Field(default=False)
    is_client: bool = Field(default=False)

    class Config:
        extra = Extra.ignore


class PayPal(BaseModel):
    uid: str
    paypal_email: str

    class Config:
        extra = Extra.ignore



