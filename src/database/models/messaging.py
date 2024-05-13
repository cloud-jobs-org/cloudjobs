from enum import Enum

from pydantic import BaseModel, Field
from datetime import datetime

from src.utils import create_id


def date_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class RecipientTypes(Enum):
    EMPLOYEES = "Employees"
    CLIENTS = "Policy Holders"
    LAPSED_POLICY = "Lapsed Policy - Policy Holders"

    @classmethod
    def get_fields(cls):
        """Return a list of field names."""
        return [field.value for field in cls]


class SMSCompose(BaseModel):
    message_id: str = Field(default_factory=create_id)
    reference: str | None
    message: str
    from_cell: str | None
    to_cell: str | None
    to_branch: str
    recipient_type: str
    date_time_composed: str = Field(default_factory=date_time)
    date_time_sent: str | None
    is_delivered: bool = Field(default=False)
    client_responded: bool = Field(default=False)


class SMSInbox(BaseModel):
    message_id: str = Field(default_factory=create_id)
    to_branch: str
    parent_reference: str | None
    from_cell: str | None
    is_response: bool = Field(default=True)
    previous_history: str | None
    message: str
    date_time_received: str = Field(default_factory=date_time)
    is_read: bool = Field(default=False)


class EmailCompose(BaseModel):
    message_id: str = Field(default_factory=create_id)
    from_email: str | None
    to_email: str | None
    subject: str
    message: str
    to_branch: str
    recipient_type: str


class ContactForm(BaseModel):
    uid: str
    contact_id: str = Field(default_factory=create_id)
    original_contact_id: str | None
    name: str
    email: str
    message: str
    datetime_submitted: str = Field(default_factory=date_time)
    issue_resolved: bool = Field(default=False)


class Ticket(BaseModel):
    ticket_id: str
    original_contact_id: str | None
