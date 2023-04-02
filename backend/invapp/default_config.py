import os
from datetime import timedelta
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
URI ="sqlite:///" + os.path.join(base_dir, "database.db")
load_dotenv(".env", verbose=True)
DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE", URI)
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
SECRET_KEY = os.environ.get("APP_SECRET_KEY")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
API_TITLE="Inventory REST API"
API_VERSION="v1"
OPENAPI_VERSION="3.0.3"
OPENAPI_URL_PREFIX= "/"
OPENAPI_SWAGGER_UI_PATH="/swagger-ui"  # for documentation purposes..http://localhost:7005{port no}/swagger-ui
OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
OPENAPI_REDOC_PATH="/redoc"
OPENAPI_REDOC_URL="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
OPENAPI_RAPIDOC_PATH="/rapidoc"
OPENAPI_RAPIDOC_URL="https://unpkg.com/rapidoc/dist/rapidoc-min.js"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
#UPLOADED_IMAGES_DEST= os.path.join("static", "images")
#UPLOAD_FOLDER="static"
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

