from flask import Flask


def register_routes(app: Flask):
    from src.routes.home import home_route
    from src.routes.auth import auth_route
    from src.routes.jobs import jobs_route
    from src.routes.admin import admin_route
    from src.routes.seo import seo_route

    routes = [auth_route, home_route, jobs_route, admin_route, seo_route]
    for route in routes:
        app.register_blueprint(route)
