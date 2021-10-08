import pytest
from flask import current_app

from app import app


@pytest.fixture
def client():
    with app.app_context():
        current_app.config['SERVER_NAME'] = 'example.com'
    with app.test_client() as client:
        yield client
