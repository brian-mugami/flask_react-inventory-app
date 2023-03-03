import pytest
from invapp import create_app
from invapp.db import db
@pytest.fixture()
def app():
    app = create_app("sqlite:///")
    with app.app_context():
        db.create_all()

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()