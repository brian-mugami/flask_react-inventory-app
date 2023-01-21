import os.path
from datetime import timedelta
from .methods import userblueprint, itemsblueprint, supplierblueprint, customerblueprint

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from .db import db
from flask_migrate import Migrate
import secrets
from dotenv import load_dotenv
from .blocklist import TokenBlocklist

basedir = os.path.abspath(os.path.dirname(__file__))
migrate = Migrate()
ACCESS_EXPIRES = timedelta(hours=1)

def create_app():
    load_dotenv()
    app = Flask(__name__)
    secret = secrets.token_urlsafe(23)
    app.secret_key = secret
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Inventory REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"  # for documentation purposes..http://localhost:7005{port no}/swagger-ui
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["OPENAPI_REDOC_PATH"] = "/redoc"
    app.config["OPENAPI_REDOC_URL"] = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    app.config["OPENAPI_RAPIDOC_PATH"] = "/rapidoc"
    app.config["OPENAPI_RAPIDOC_URL"] = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"

    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:mugami@localhost:5432/Inventory"
    app.config['TRACK MODIFICATIONS'] = False
    db.init_app(app)

    api = Api(app)
    migrate.init_app(app, db)

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
    app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(16)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

        return token is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwtpayload):
        return (
            jsonify(
                {"description":"token was revoked", "error":"token revoked"}
            ), 401
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header,jwt_payload):
        return (
            jsonify({"message":"Token has expired", "error":"Token_expired"}),
            401
        )

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_loader(jwt_header,jwt_payload):
        return (
            jsonify(
                {"description": "token is not fresh",
                "error":"fresh_token_required"}
            )
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message":"Signature verification failed", "error":"Invalid_token"}),
            401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description":"Request does not contain an access token",
                    "error":"authorization required"
                }
            ), 401
        )
    @app.before_first_request
    def create_tables():
        db.create_all()

    api.register_blueprint(userblueprint)
    api.register_blueprint(itemsblueprint)
    api.register_blueprint(supplierblueprint)
    api.register_blueprint(customerblueprint)
    return app

#def create_database(db):
 #   if not os.path.join("sqlite:///"+os.path.join(basedir, os.getenv("DATABASE"))):
  #      db.create_all()
   #     return "database created successfully"
