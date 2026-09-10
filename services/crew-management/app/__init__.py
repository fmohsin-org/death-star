from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()


def create_app(config_name=None):
    """Application factory for Death Star Crew Management service."""
    app = Flask(__name__, template_folder="templates")

    app.config.from_object("config.Config")
    app.secret_key = "imperial-crew-mgmt-secret-f4a7b3c9d6e"
    app.debug = True

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    db.init_app(app)

    from app.routes.personnel import personnel_bp
    from app.routes.auth import auth_bp
    from app.routes.cross_repo import cross_repo_bp

    app.register_blueprint(personnel_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cross_repo_bp)

    with app.app_context():
        db.create_all()

    @app.after_request
    def add_headers(response):
        response.headers["Server"] = "DeathStar-CrewMgmt/2.1.4"
        response.headers["X-Powered-By"] = "Imperial-Flask"
        return response

    return app
