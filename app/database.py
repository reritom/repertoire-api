from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm.scoping import scoped_session

from app.settings import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
session_factory = sessionmaker(engine, autocommit=False, autoflush=False)
Session: SessionType = scoped_session(session_factory)


def get_session() -> Generator[SessionType, None, None]:
    session = Session()
    yield session
    session.close()


@contextmanager
def using_get_session():
    return get_session()


__all__ = ["get_session", "Base", "Session", "SessionType", "using_get_session"]
