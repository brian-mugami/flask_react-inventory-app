import json

from invapp.models import UserModel
##python -m pytest -v
##python -m pytest tests/unit
##python -m pytest --last-failed
##python -m pytest --setup-show
##python -m pytest --cov=project


def test_register(client, app):
    data = {"first_name": "brian", "last_name": "mugami", "email": "test@test.com", "password": "test"}
    response = client.post("/register",data=data , headers={"Content-Type": "application/json"})

    with app.app_context():
        assert UserModel.query.count() == 1
