import hashlib
import hmac

from flask import Flask, url_for
from paypalrestsdk import configure, Api, Payment
from src.config import Settings
from src.controller import Controllers
from src.database.models.users import User, PayPal


class PayPalController(Controllers):
    def __init__(self):
        super().__init__()
        self.mode = "live"
        self._client_secret = ""

    def init_app(self, app: Flask, config_instance: Settings):
        self._client_secret = config_instance.PAYPAL_SETTINGS.SECRET_KEY
        configure({
            "mode": self.mode,
            "client_id": config_instance.PAYPAL_SETTINGS.CLIENT_ID,
            "client_secret": config_instance.PAYPAL_SETTINGS.SECRET_KEY
        })
        # self.api = Api(**{
        #     "mode": self.mode,
        #     "client_id": config_instance.PAYPAL_SETTINGS.CLIENT_ID,
        #     "client_secret": config_instance.PAYPAL_SETTINGS.SECRET_KEY
        # })
        super().init_app(app=app)

    async def create_payment(self, amount: int, user: User, paypal: PayPal,
                             success_url: str, failure_url: str) -> tuple[Payment, bool]:
        """
        :param failure_url:
        :param success_url:
        :param paypal:
        :param user:
        :param amount: The amount of the payment
        :param customer_info: Information about the customer
        :param uid: User ID to be included
        :return: A tuple containing the Payment object and a boolean indicating success or failure
        """

        # Include customer information and UID
        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": success_url,
                "cancel_url": failure_url
            },
            "transactions": [{
                "amount": {
                    "total": amount,
                    "currency": "USD"
                },
                "description": f"Deposit to wallet : {user.uid}"
            }],
        })

        return payment, payment.create()

    async def verify_signature(self, payload: str, signature: str) -> bool:
        """

        :param signature:
        :return:
        """
        expected_sig = hmac.new(
            bytes(self._client_secret, 'utf=8'),
            bytes(payload, 'utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, signature)
