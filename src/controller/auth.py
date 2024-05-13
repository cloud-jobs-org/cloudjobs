import random
import string
import time
import uuid

from flask import Flask, render_template
from pydantic import ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from src.controller import error_handler, UnauthorizedError, Controllers
from src.database.models.profile import Profile, ProfileUpdate
from src.database.models.users import User, CreateUser, UserUpdate, PayPal
from src.database.sql.user import UserORM, PayPalORM
from src.emailer import EmailModel
from src.main import send_mail
import requests


class UserController(Controllers):

    def __init__(self):
        super().__init__()

        self._time_limit = 360
        self._verification_tokens: dict[str, int | dict[str, str | int]] = {}
        self.profiles: dict[str, Profile] = {}
        self.users: dict[str, User] = {}

    def init_app(self, app: Flask):
        super().init_app(app=app)

    async def manage_users_dict(self, new_user: User):
        # Check if the user instance already exists in the dictionary
        self.users[new_user.uid] = new_user

    async def manage_profiles(self, new_profile: Profile):
        self.profiles[new_profile.uid] = new_profile

    @error_handler
    async def add_paypal(self, user: User, paypal_email: str) -> PayPal | None:
        """

        :param user:
        :param paypal_email:
        :return:
        """
        paypal_email = paypal_email.strip().lower()
        if not paypal_email:
            return None

        with self.get_session() as session:
            paypal_account = session.query(PayPalORM).filter(PayPalORM.paypal_email == paypal_email).first()
            if isinstance(paypal_account, PayPalORM):
                if paypal_account.uid == user.uid:
                    paypal_account.paypal_email = paypal_email
                    paypal_account.uid = user.uid
                    session.merge(paypal_account)
                    session.commit()
                    return PayPal(**paypal_account.to_dict())
                else:
                    return None

            paypal_account: PayPalORM = session.query(PayPalORM).filter(PayPalORM.uid == user.uid).first()
            if isinstance(paypal_account, PayPalORM):
                paypal_account.paypal_email = paypal_email
                paypal_account_ = PayPal(**paypal_account.to_dict())
                session.merge(paypal_account_)
                session.commit()

                return paypal_account_

            paypal_orm = PayPalORM(paypal_email=paypal_email, uid=user.uid)
            paypal_account_ = PayPal(**paypal_orm.to_dict())
            session.add(paypal_orm)
            session.commit()
            return paypal_account_

    @error_handler
    async def get_paypal_account(self, uid: str) -> PayPal | None:
        with self.get_session() as session:
            paypal_account: PayPalORM = session.query(PayPalORM).filter(PayPalORM.uid == uid).first()
            print("PAYPAL ACCOUNT")
            print(paypal_account)
            if isinstance(paypal_account, PayPalORM):
                return PayPal(**paypal_account.to_dict())
            return None

    async def is_token_valid(self, token: str) -> bool:
        """
        **is_token_valid**
            Checks if the password reset token is valid based on the elapsed time.
        :param token: The password reset token to validate.
        :return: True if the token is valid, False otherwise.
        """
        if token in set(self._verification_tokens.keys()):
            timestamp: int = self._verification_tokens[token]
            current_time: int = int(time.time())
            elapsed_time = current_time - timestamp
            return elapsed_time < self._time_limit

        return False

    @error_handler
    async def get(self, uid: str) -> dict[str, str] | None:
        """
        :param uid:
        :return:
        """
        if not uid:
            return None
        # if uid in self.users:
        #     return self.users[uid].dict()

        with self.get_session() as session:
            user_data: UserORM = session.query(UserORM).filter(UserORM.uid == uid).first()
            return user_data.to_dict()

    @error_handler
    async def get_by_email(self, email: str) -> User | None:
        """
            **get_by_email**
        :param email:
        :return:
        """
        if not email:
            return None
        # for user in self.users.values():
        #     if user.email.casefold() == email.casefold():
        #         return user

        with self.get_session() as session:
            user_data: UserORM = session.query(UserORM).filter(UserORM.email == email.casefold()).first()

            return User(**user_data.to_dict()) if user_data else None

    @error_handler
    async def send_password_reset(self, email: str) -> dict[str, str] | None:
        """
        Sends a password reset email to the specified email address.

        :param email: The email address to send the password reset email to.
        :return: A dictionary containing the result of the email sending operation, or None if an error occurred.
        """
        # TODO please complete the method to send the password reset email
        password_reset_subject: str = "last-shelter.vip Password Reset Request"
        # Assuming you have a function to generate the password reset link
        password_reset_link: str = self.generate_password_reset_link(email)

        html = f"""
        <html>
        <body>
            <h2>Funeral Manager - funeral.org</h2>
            <p>Hello,</p>
            <p>We received a password reset request for your https://funeral-manager.org account. 
            Please click the link below to reset your password:</p>
            <a href="{password_reset_link}">{password_reset_link}</a>
            <p>If you didn't request a password reset, you can ignore this email.</p>
            <p>Thank you,</p>
            <p>The Rental Manager Team</p>
        </body>
        </html>
        """

        email_template = dict(to_=email, subject_=password_reset_subject, html_=html)
        await send_mail.send_mail_resend(email=EmailModel(**email_template))

        return email_template

    def generate_password_reset_link(self, email: str) -> str:
        """
        Generates a password reset link for the specified email.

        :param email: The email address for which to generate the password reset link.
        :return: The password reset link.
        """
        token = str(uuid.uuid4())  # Assuming you have a function to generate a random token
        self._verification_tokens[token] = int(time.time())
        password_reset_link = f"https://funeral-manager.org/admin/reset-password?token={token}&email={email}"

        return password_reset_link

    async def post(self, user: CreateUser) -> User | None:
        """

        :param user:
        :return:
        """
        with self.get_session() as session:

            user_data: UserORM = session.query(UserORM).filter(or_(UserORM.uid == user.uid,
                                                                   UserORM.email == user.email)).first()
            if user_data:
                return None
            user_ = User(**user.to_dict())
            new_user: UserORM = UserORM(**user_.dict())
            session.add(new_user)
            new_user_dict = new_user.to_dict()
            session.commit()
            _user_data = User(**new_user_dict) if isinstance(new_user, UserORM) else None
            self.users[_user_data.uid] = _user_data
            return _user_data

    @error_handler
    async def put(self, user: User) -> dict[str, str] | None:
        with self.get_session() as session:
            user_data: UserORM = session.query(UserORM).filter_by(uid=user.uid).first()
            if not user_data:
                return None

            # Update user_data with the values from the user Pydantic BaseModel
            for field in user_data.__table__.columns.keys():
                if hasattr(user, field):
                    setattr(user_data, field, getattr(user, field))

            # Save the updated user_data back to the session
            session.add(user_data)
            session.commit()
            self.users[user_data.uid] = User(**user_data.to_dict())
            return user_data.to_dict()

    @error_handler
    async def login(self, email: str, password: str) -> User | None:
        with self.get_session() as session:
            print(f"Email : {email}")
            user_data: UserORM = session.query(UserORM).filter(UserORM.email == email).first()
            try:
                if user_data:
                    user: User = User(**user_data.to_dict())
                else:
                    return None
            except ValidationError as e:
                raise UnauthorizedError(description="Cannot Login User please check your login details")
            return user if user.is_login(password=password) else None

    async def add_employee(self, user: User) -> User | None:
        """
        Add or update a user in the database.

        :param user: User details to add or update.
        :return: The added or updated user details.
        """
        with self.get_session() as session:
            email = user.email.lower().strip()
            user_data: UserORM = session.query(UserORM).filter_by(email=email).first()
            if user_data:
                # Update user data if user exists
                user_data.uid = user.uid
                user_data.branch_id = user.branch_id
                user_data.company_id = user.company_id
                user_data.username = user.username
                user_data.password_hash = user.password_hash
                user_data.account_verified = user.account_verified
                user_data.is_system_admin = user.is_system_admin
                user_data.is_company_admin = user.is_company_admin
                user_data.is_employee = user.is_employee
                user_data.is_client = user.is_client

            else:
                # Create new user if user does not exist
                new_user = UserORM(**user.dict(exclude_unset=True))  # Exclude unset fields
                session.add(new_user)

            try:
                session.commit()
                return user
            except IntegrityError:
                # Handle integrity error (e.g., duplicate email)
                session.rollback()
                return None

    @error_handler
    async def send_verification_email(self, user: User, password: str) -> None:
        """
        Sends a verification email to the specified user.

        :param user: The user to send the verification email to.
        """
        token = str(uuid.uuid4())  # Assuming you have a function to generate a verification token
        verification_link = f"https://funeral-manager.org/dashboard/verify-email?token={token}&email={user.email}"
        self._verification_tokens[token] = dict(email=user.email, timestamp=int(time.time()))
        # Render the email template
        email_html = render_template("email_templates/verification_email.html", user=user,
                                     verification_link=verification_link, password=password)

        msg = EmailModel(subject_="last-shelter.vip Email Verification",
                         to_=user.email,
                         html_=email_html)

        await send_mail.send_mail_resend(email=msg)

    @error_handler
    async def verify_email(self, email: str, token: str) -> bool:
        """
            **verify_email**
        :param email:
        :param token:
        :return:
        """
        if email is None:
            return False
        if token is None:
            return False
        if token not in self._verification_tokens:
            return False

        _data: dict[str, str | int] = self._verification_tokens[token]

        current_time: int = int(time.time())
        elapsed_time = current_time - int(_data.get('timestamp', 0))
        return (elapsed_time < self._time_limit) and (email.casefold() == _data.get('email'))

    @error_handler
    async def get_all_accounts(self) -> list[User]:
        with self.get_session() as session:
            accounts_list = session.query(UserORM).all()
            return [User(**account.to_dict()) for account in accounts_list if account]

    @error_handler
    async def get_account_by_uid(self, uid: str) -> User | None:
        with self.get_session() as session:
            account_orm = session.query(UserORM).filter(UserORM.uid == uid).first()
            if isinstance(account_orm, UserORM):
                return User(**account_orm.to_dict())
            return None

    @staticmethod
    async def create_employee_password():
        """

        :return:
        """
        random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        # Convert all letters to uppercase
        return random_chars.lower()
