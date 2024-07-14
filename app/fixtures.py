from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from app.application import create_app
from app.auth.routers.dependencies import get_authenticated_user
from app.database import Session, engine, get_session


@pytest.fixture(scope="function")
def session():
    connection = engine.connect()
    transaction = connection.begin()
    Session.configure(bind=connection, binds={})

    yield Session()

    transaction.rollback()
    connection.close()
    Session.close()
    Session.remove()
    engine.dispose()


@pytest.fixture(scope="function")
def app():
    return create_app()


@pytest.fixture(scope="function")
def client(session, app):
    client = TestClient(app)
    session = Session()
    app.dependency_overrides[get_session] = lambda: session
    return client


@pytest.fixture(scope="function")
def using_user(app):
    @contextmanager
    def _using_user(user):
        app.dependency_overrides[get_authenticated_user] = lambda: user
        yield

    return _using_user
