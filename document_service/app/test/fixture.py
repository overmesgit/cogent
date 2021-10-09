import pytest
from flask import current_app
from redis import Redis

from app.app import app

redis_con = Redis(host='redis')


@pytest.fixture
def wipe_db():
    redis_con.flushall()


@pytest.fixture
def client(wipe_db):
    with app.app_context():
        current_app.config['SERVER_NAME'] = 'example.com'
    with app.test_client() as client:
        yield client
