from .resources import (userblueprint, itemsblueprint, supplierblueprint,
                        customerblueprint, confirmationblueprint, purchaseaccountsblueprint,
                        paymentaccountsblueprint, salesaccountblueprint, expenseaccountingblueprint, invoiceblueprint,
                        receiptblueprint, bankbalanceblueprint, inventorybalanceblueprint, customerbalanceblueprint,
                        supplierbalanceblueprint, inventoryadjustmentblueprint, transactionblueprint, catchallblueprint, reportsblueprint, uploadsblueprint)
from .tranx_resources import purchasingblueprint, paymentblueprint, salesblueprint, customerpaymentblueprint
from flask import Flask, jsonify, render_template
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .db import db
from flask_migrate import Migrate
from dotenv import load_dotenv
from .blocklist import TokenBlocklist

migrate = Migrate()
cors = CORS()


def create_app():
    # change application settings to config for prod
    app = Flask(__name__, static_folder='static', template_folder='templates')
    load_dotenv(".env", verbose=True)

    #app.config.from_object("invapp.config")
    #app.config.from_envvar("APPLICATION_SETTINGS")
    app.config.from_pyfile("config.py")
    db.init_app(app)
    api = Api(app)
    cors.init_app(app, resources={r"*": {"origins": "*"}})
    migrate.init_app(app, db)
    jwt = JWTManager(app)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template("index.html")

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

        return token is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwtpayload):
        return (
            jsonify(
                {"description": "token was revoked", "error": "token revoked"}
            ), 401
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "Token has expired", "error": "Token_expired"}),
            401
        )

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_loader(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "token is not fresh",
                 "error": "fresh_token_required"}
            )
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message": "Signature verification failed", "error": "Invalid_token"}),
            401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token",
                    "error": "authorization required"
                }
            ), 401
        )
    with app.app_context():
        db.create_all()

    api.register_blueprint(userblueprint)
    api.register_blueprint(itemsblueprint)
    api.register_blueprint(supplierblueprint)
    api.register_blueprint(customerblueprint)
    api.register_blueprint(confirmationblueprint)
    api.register_blueprint(purchasingblueprint)
    api.register_blueprint(paymentaccountsblueprint)
    api.register_blueprint(purchaseaccountsblueprint)
    api.register_blueprint(paymentblueprint)
    api.register_blueprint(salesblueprint)
    api.register_blueprint(salesaccountblueprint)
    api.register_blueprint(customerpaymentblueprint)
    api.register_blueprint(expenseaccountingblueprint)
    api.register_blueprint(invoiceblueprint)
    api.register_blueprint(receiptblueprint)
    api.register_blueprint(bankbalanceblueprint)
    api.register_blueprint(inventorybalanceblueprint)
    api.register_blueprint(customerbalanceblueprint)
    api.register_blueprint(supplierbalanceblueprint)
    api.register_blueprint(inventoryadjustmentblueprint)
    api.register_blueprint(transactionblueprint)
    api.register_blueprint(reportsblueprint)
    api.register_blueprint(uploadsblueprint)

    return app
