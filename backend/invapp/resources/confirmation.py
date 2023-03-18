import traceback
from time import time

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..libs.send_emails import MailgunException
from ..schemas.confirmationschema import ConfirmationSchema
from ..models.usermodels import ConfirmationModel, UserModel
from flask import render_template, make_response

blp = Blueprint("Confirmation", __name__, description="Confirmation on users")

@blp.route("/confirmation/<string:confirmation_id>")
class Confirmation(MethodView):
    def get(self, confirmation_id):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            abort(400, message="Confirmation not found")
        if confirmation.expired:
            abort(409, message="Confirmation expired")
        if confirmation.confirmed:
            abort(409, message="Confirmation is already confirmed")
        confirmation.confirmed = True
        confirmation.save_to_db()
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirmation.html", email=confirmation.user.email, confirmation_id=confirmation.id), 200, headers)


@blp.route("/user/confirmation/<int:user_id>")
class ConfirmationByUser(MethodView):
    @blp.response(200, ConfirmationSchema)
    @classmethod
    def get(self, user_id):
        user = UserModel.find_user_by_id(user_id)
        return (
            {
                "current_time":int(time()),
                "confirmation":[each for each in user.confirmation.order_by(ConfirmationModel.expire_at)]
            }
        )

    def post(self, user_id:int):
        user = UserModel.find_user_by_id(user_id)
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    abort(400, message="Already confirmed")
                confirmation.force_to_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()

            return {"message":"Resend succesfull"}, 200
        except MailgunException as e:
            abort(500, message=f"{str(e)}")
        except:
            traceback.print_exc()
            abort(500, message="Resend failed")
