from flask import Flask, g, render_template
from flask_mysqldb import MySQL
from app.routes.admin import admin
from app.routes.user import user
from app.routes.pay import pay
from app.routes.api import api
from app.routes.landing import landing
from app.helpers.authdata import auth_data
from app.helpers.helpers import get_media
from config import Config
from app.utils.mailer import send_email

db = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MySQL
    db.init_app(app)

    # Set the email function globally
    @app.before_request
    def set_mailer():
        g.send_email = send_email

    # Global database connection
    @app.before_request
    def set_db():
        g.db = db

    # App-wide context processors
    @app.context_processor
    def inject_globals():
        return {"auth_data": auth_data(), "get_media": get_media}

    # Clear cache to avoid stale content
    @app.after_request
    def disable_cache(response):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # Register Blueprints
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(pay, url_prefix="/pay")
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(landing, url_prefix="/")

    # Global 404 Error Handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    return app
