from datetime import datetime
from datetime import timezone

from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from ..models.usermodels import UserModel
from ..db import db
from ..schemas import UserSchema,LoginSchema
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required,get_jwt, get_jwt_identity
from ..blocklist import TokenBlocklist

blp = Blueprint("Users", __name__, description="Operations on users")

@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(email=user_data["email"]).first()
        if user:
            abort(409, message="User already exists")

        user = UserModel(email=user_data["email"],first_name=user_data["first_name"],last_name=user_data["last_name"],
                        password=generate_password_hash(user_data["password"], 'sha256'))
        db.session.add(user)
        db.session.commit()

        return user

@blp.route("/user/<int:id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, id):
        user = UserModel.query.get_or_404(id)
        return user

    @blp.response(200, UserSchema)
    def delete(self, id):
        user = UserModel.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()

        return user

    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    def put(self,user_data, id):
        user = UserModel.query.get_or_404(id)
        if user:
            user.first_name = user_data["first_name"]
            user.last_name = user_data["last_name"]
            user.profile_image = user_data["profile_image"]
            user.email = user_data["email"]
            user.password = user_data["password"]
            db.session.commit()
            return user

        else:
            abort(409, message="User not valid")

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(email=user_data["email"]).first()

        if user and check_password_hash(user.password, user_data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify({"refresh token": refresh_token, "access_token":access_token})

        abort(401, message="Invalid credentials")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()
        return jsonify(msg="JWT revoked")


@blp.route("/users")
class UserView(MethodView):
    @blp.response(200, UserSchema(many=True))
    def get(self):
        users = UserModel.query.all()
        return users