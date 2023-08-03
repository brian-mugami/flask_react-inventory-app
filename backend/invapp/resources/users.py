import traceback
from datetime import datetime
from datetime import timezone

from flask import jsonify, redirect, render_template, flash
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..Forms.admin_registration import AdminRegistrationForm
from ..models.masters.usermodels import UserModel, ConfirmationModel
from ..db import db
from ..schemas.userschema import UserSchema, LoginSchema, UserUpdateSchema, PaswordChangeSchema
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from ..blocklist import TokenBlocklist
from ..libs.send_emails import MailgunException

blp = Blueprint("Users", __name__, description="Operations on users")


@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(email=user_data["email"]).first()
        if user:
            abort(409, message="User with set email already exists!!")

        if len(user_data['password1']) < 6:
            abort(417, message="Password should be longer than 6 characters!!")
        if user_data['password1'] != user_data['password2']:
            abort(409, message="Passwords have to match!!")
        try:
            user = UserModel(email=user_data["email"], first_name=user_data["first_name"],
                             last_name=user_data["last_name"],
                             password=generate_password_hash(user_data["password1"], 'sha256'))
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": "User created successfully"}
        except MailgunException as e:
            user.delete_from_db()
            abort(500, message=f"{str(e)}")
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": "Failed to create user"}


@blp.route("/user/<int:id>")
class User(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, UserSchema)
    def get(self, id):
        user_id = get_jwt_identity()
        user = UserModel.query.get(user_id)
        if not user.is_admin:
            abort(400, message="Only the admin is allowed to perform this action")
        user = UserModel.query.get_or_404(id)
        return user

    @jwt_required(fresh=True)
    @blp.response(200, UserSchema)
    def delete(self, id):
        user_id = get_jwt_identity()
        user = UserModel.query.get(user_id)
        if not user.is_admin:
            abort(400, message="Only the admin is allowed to perform this action")
        user = UserModel.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()

        return {"message", "deleted"}, 204

    @jwt_required(fresh=True)
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def patch(self, user_data, id):
        user_id = get_jwt_identity()
        user = UserModel.query.get(user_id)
        if not user.is_admin:
            abort(400, message="Only the admin is allowed to perform this action")
        user = UserModel.query.get_or_404(id)
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.email = user_data["email"]
        user.password = generate_password_hash(user_data.get("password"), 'sha256')
        user.is_active = user_data.get("is_active")
        db.session.commit()
        return jsonify({"message": "User updated"})


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(email=user_data["email"]).first()
        if not user or not user.is_active:
            abort(400, message='You are not allowed to login')
        if user and check_password_hash(user.password, user_data["password"]):
            confirmation = user.most_recent_confirmation
            if (confirmation and confirmation.confirmed) or user.is_admin:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(identity=user.id)
                user.last_login = datetime.utcnow()
                db.session.commit()
                return jsonify({"refresh_token": refresh_token, "access_token": access_token})
            abort(500, message=f"{user.email} not confirmed , please confirm in your mail")
        abort(401, message="Invalid credentials")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required(fresh=True)
    def delete(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()
        return jsonify(msg="JWT revoked")


@blp.route("/users")
class UserView(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, UserSchema(many=True))
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.get(user_id)
        if not user.is_admin:
            abort(400, message="Only the admin is allowed to perform this action")
        users = UserModel.query.all()
        return users


@blp.route("/user/password")
class PasswordChangeView(MethodView):
    @blp.arguments(PaswordChangeSchema)
    def post(self, data):
        user = UserModel.query.filter_by(email=data["email"]).first()
        if not user:
            abort(404, message="User does not exist")

        if len(data["password1"]) < 0:
            abort(400, message="Password must not be empty")
        if data["password1"] != data["password2"]:
            abort(400, message="Passwords do not match!!")
        user.password = generate_password_hash(data["password2"], 'sha256')
        db.session.commit()

        return jsonify({"message": "Password Changed"})


@blp.route("/register/user/admin", methods=["GET", "POST"])
class UserAdminPage(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, data):
        user = UserModel.query.filter_by(email=data.get("email")).first()
        if user:
            abort(400, message="User with set email already exists!!")
        if len(data.get("password1")) < 6:
            abort(400, message="User with set email already exists!!")
        elif data.get("password1") != data.get("password2"):
            abort(400, message="Passwords do not match")
        else:
            user = UserModel(email=data.get("email"), first_name=data.get("first_name"),
                             last_name=data.get("last_name"),
                             password=generate_password_hash(data.get("password1"), 'sha256'), is_admin=True)
            db.session.add(user)
            db.session.commit()

            return user
