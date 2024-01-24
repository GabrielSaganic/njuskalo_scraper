import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_HOST = os.environ.get("DB_HOST", "")
DB_NAME = os.environ.get("DB_NAME", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_USERNAME = os.environ.get("DB_USERNAME", "")
DEBUG = os.environ.get("DEBUG", False)
DATABASE_URL = (
    os.environ.get("DATABASE_URL", "")
    if DEBUG == "True"
    else f"mysql+mysqlconnector://{DB_NAME}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# use session_factory() to get a new Session
_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()
