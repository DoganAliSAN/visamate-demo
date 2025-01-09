from .routes.auth_routes import auth_bp
from .routes.main_routes import main_bp
from .routes.admin_routes import admin_bp
from .routes.customer_routes import customer_bp
from flask import Flask
from .routes.functions import get_app

def create_app():
    app = get_app()


    ROLES = {
        "SuperAdmin":"SuperAdmin",
        "Admin":"Admin",
        "Customer":"Customer"
    }



    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)

    return app