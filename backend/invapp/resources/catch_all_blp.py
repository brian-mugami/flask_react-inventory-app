from flask import render_template
from flask_smorest import Blueprint

blp = Blueprint('catch_all', __name__)

# Add the catch-all route
@blp.route('/', defaults={'path': ''})
@blp.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")

