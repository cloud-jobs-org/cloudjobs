from flask import Flask
from flask_socketio import SocketIO
from src.controller.encryptor import Encryptor

from src.emailer import SendMail

from src.utils import format_with_grouping, friendlytimestamp

encryptor = Encryptor()
send_mail = SendMail()

from src.controller.auth import UserController
from src.controller.customers_controller import CustomerController
from src.controller.orders_controller import OrdersController
from src.controller.paypal_controller import PayPalController
from src.controller.chat_controller import ChatController
from src.controller.messaging_controller import MessagingController
from src.controller.product_controller import ProductController
# from src.firewall import Firewall

user_controller = UserController()
customer_controller = CustomerController()
orders_controller = OrdersController()
paypal_controller = PayPalController()
chat_controller = ChatController()
messaging_controller = MessagingController()
product_controller = ProductController()

chat_io = SocketIO()


# firewall = Firewall()


def _add_filters(app: Flask):
    """
        **add_filters**
            filters allows formatting from models to user readable format
    :param app:
    :return:
    """
    app.jinja_env.filters['number'] = format_with_grouping
    app.jinja_env.filters['time'] = friendlytimestamp


def create_app(config):
    from src.utils import template_folder, static_folder
    app: Flask = Flask(__name__)
    app.template_folder = template_folder()
    app.static_folder = static_folder()
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['BASE_URL'] = "https://zwavhudivhudi-electrical.work"

    with app.app_context():
        from src.main.bootstrapping import bootstrapper
        from src.routes import register_routes
        bootstrapper()
        # firewall.init_app(app=app)
        register_routes(app=app)
        _add_filters(app)

        encryptor.init_app(app=app)
        chat_io.init_app(app)
        user_controller.init_app(app=app)
        customer_controller.init_app(app=app)
        orders_controller.init_app(app=app)
        paypal_controller.init_app(app=app, config_instance=config)
        product_controller.init_app(app=app)
        # chat_controller.init_app(app=app)
        # messaging_controller.init_app(app=app)

    return app
