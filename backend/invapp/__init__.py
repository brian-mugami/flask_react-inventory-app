import os.path
from .libs.image_helper import IMAGE_SET
from .resources import userblueprint, itemsblueprint, supplierblueprint, customerblueprint, imageblueprint
from flask import Flask, jsonify
from flask_uploads import configure_uploads,patch_request_class
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .db import db
from flask_migrate import Migrate
from dotenv import load_dotenv
from .blocklist import TokenBlocklist

basedir = os.path.abspath(os.path.dirname(__file__))
migrate = Migrate()
cors = CORS()

def create_app():
    #change application settings to config for prod
    app = Flask(__name__)
    load_dotenv(".env", verbose=True)

    app.config.from_object("invapp.default_config")
    app.config.from_envvar("APPLICATION_SETTINGS")
    patch_request_class(app, 10 * 1024 * 1024) #10mb max size upload
    configure_uploads(app, IMAGE_SET)

    db.init_app(app)
    api = Api(app)
    cors.init_app(app, resources={r"*": {"origins": "*"}})
    migrate.init_app(app, db)
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
    api.register_blueprint(imageblueprint)
    return app

#def create_database(db):
 #   if not os.path.join("sqlite:///"+os.path.join(basedir, os.getenv("DATABASE"))):
  #      db.create_all()
   #     return "database created successfully"
