import pytest

from app.database import Session, engine


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
