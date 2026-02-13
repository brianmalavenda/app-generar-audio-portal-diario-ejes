import pytest
from api_backend import create_app  # Importamos la fábrica

@pytest.fixture
def app():
    app = create_app(config_name='testing')
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
