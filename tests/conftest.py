from flask import Flask
import pytest

from server import app

# @pytest.fixture
# def client(): 
# 	app = Flask(__name__.split('.')[0])
# 	app.secret_key = 'something_special'

# 	with app.test_client() as client:
# 	        yield client

@pytest.fixture()
def client():
    return app.test_client()

