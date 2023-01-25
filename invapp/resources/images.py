from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import send_file
import traceback
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..libs import image_helper
from ..schemas.imageschema import ImageSchema
from flask_uploads import UploadNotAllowed

blp = Blueprint("Image", __name__, description="Image operations")
@blp.route("/image/upload")
class ImageResource(MethodView):

    @jwt_required(fresh=True)
    @blp.arguments(ImageSchema, location="files")
    def post(self, data):
        """Used to upload an image file.
        uses JWT to retrieve user info and then saves image to users folder.
        If there is duplicate filenames it appends a number at the end"""
        image = data["file_1"]
        user_id = get_jwt_identity()
        folder = f"user_{user_id}" #static/images/user_1
        try:
            image_path = image_helper.save_image(image=image, folder=folder)
            basename = image_helper.get_basename(image_path)
            return {"message": f"{basename} saved successfully"}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(image)
            return {"message": f"extension {extension} is not allowed"}, 400


@blp.route("/image/<string:filename>")
class ImageView(MethodView):
    @jwt_required()
    def get(self, filename:str):
        """
        returns the requested image if it exists. Looks up inside the logged in users folder
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"message": "File name is illegal"}
        try:
            return send_file(image_helper.get_path(filename, folder))
        except FileNotFoundError:
            return {"message": "image not found"}

    @jwt_required()
    def delete(self, filename:str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"message": "File name is illegal"}
        try:
            os.remove(image_helper.get_path(filename=filename, folder=folder))
            return {"message":"Image deleted"}
        except:
            e = traceback.print_exc()
            return {"Message":f"{e} and image is not found"}

@blp.route("/user/avatar")
class AvatarMethod(MethodView):
    """
    This endpoint is used to upload a users avatar. All avatars are named after the user,s ID(user_id.ext)
    Uploading a new avatar overwrites an existing one
    """
    @jwt_required(fresh=True)
    @blp.arguments(ImageSchema, location="files")
    def put(self, data):
        user = get_jwt_identity()
        data = data["file_1"]
        filename = f"user_{user}"
        folder = "avatars"
        avatar_path = image_helper.find_image_in_any_format(filename=filename, folder=folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": "Image delete failed"}, 500

        try:
            ext = image_helper.get_extension(data.filename)
            avatar = filename + ext
            avatar_path = image_helper.save_image(data, folder=folder, name=avatar)
            basename = image_helper.get_basename(avatar_path)
            return {"Message": f"Avatar of basename {basename} uploaded"}
        except UploadNotAllowed:
            extension = image_helper.get_extension(data)
            return {"Message": f"{extension} not allowed"}

@blp.route("/avatar/<int:user_id>")
class Avatar(MethodView):
    @jwt_required(fresh=True)
    def get(self, user_id):
        folder = "avatars"
        user = get_jwt_identity()
        if user == user_id:
            filename = f"user_{user_id}"
            avatar = image_helper.find_image_in_any_format(filename=filename, folder=folder)
            if avatar:
                send_file(avatar)
            return {"message": "Avatar not found"}
        abort(400, message="Unauthorized user")