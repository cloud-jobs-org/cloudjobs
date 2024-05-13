from pydantic import BaseModel, Field

from src.utils import create_id


class BankAccount(BaseModel):
    """
    BusinessBankAccount

    - company_id = Column(String(ID_LEN))
    - account_holder = Column(String(NAME_LEN), primary_key=True)
    - account_number = Column(String(NAME_LEN))
    - bank_name = Column(String(NAME_LEN), index=True)
    - branch = Column(String(NAME_LEN))
    - account_type = Column(String(NAME_LEN))

    """
    bank_account_id: str = Field(default_factory=create_id)

    account_holder: str = Field(..., description="The name associated with the account")
    account_number: str = Field(..., description="The unique identification number assigned to the account")
    bank_name: str = Field(..., description="The name of the bank where the account is held")
    branch: str = Field(..., description="The specific branch of the bank where the account is held")
    account_type: str = Field(..., description="The type of account, such as checking or savings")
