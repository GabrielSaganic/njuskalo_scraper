import os

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy_database.common.base import Base, session_factory
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(
        EncryptedType(
            String(length=255),
            os.environ.get("DB_ENCRYPTION_KEY", ""),
            AesEngine,
            "pkcs5",
        ),
        nullable=False,
    )
    search_config = Column(LONGTEXT)

    @classmethod
    def get_all(cls):
        session = session_factory()
        instance = session.query(cls).all()
        session.close()
        return instance

    @classmethod
    def create_user(cls, email: str, data: str = None):
        session = session_factory()
        new_user = cls(email=email, search_config=data)
        session.add(new_user)
        session.commit()
        session.close()
