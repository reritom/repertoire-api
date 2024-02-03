from app import *  # noqa # To load the models
from app.database import Base, engine
from app.fixtures import *  # noqa # To load the fixtures


def pytest_configure(config):
    Base.metadata.create_all(engine)
