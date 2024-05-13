from flask import Flask



def register_routes(app: Flask):
    from src.routes.home import home_route
    from src.routes.auth import auth_route
    from src.routes.cart import cart_route
    from src.routes.admin import admin_route

    routes = [auth_route, home_route, cart_route, admin_route]
    for route in routes:
        app.register_blueprint(route)


