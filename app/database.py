from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from app.settings import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
session_factory = sessionmaker(engine, autocommit=False, autoflush=False)
Session = scoped_session(session_factory)
