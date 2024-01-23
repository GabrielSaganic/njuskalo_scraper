import os

from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy_database.common.base import Base, session_factory
from sqlalchemy.dialects.mysql import LONGTEXT

car_config = {'car_model': ['Toyota Yaris', 'Toyota Aygo', 'Toyota iQ', 'Ford Fiesta', 'Ford Focus', 'Ford Ka', 'Ford Fusion', 'VW Polo', 'VW Up!', 'VW Golf 6', 'VW Golf 5', 'VW Golf 4', 'VW Fox', 'Fiat Punto', 'Fiat 500', 'Renault Twingo', 'Renault 5', 'Renault Clio', 'Renault 4', 'Peugeot 107', 'Peugeot 208', 'Peugeot 207', 'Peugeot 205', 'Peugeot 108', 'Peugeot 307', 'Hyundai i10', 'Hyundai i20', 'Citroën C1', 'Citroën C3', 'Citroën C2', 'Opel Corsa', 'Seat Ibiza', 'Seat Leon', 'Seat Mii', 'Seat Altea', 'Nissan Note', 'Nissan Micra', 'Suzuki Celerio', 'Suzuki Alto', 'Kia Picanto', 'Kia Venga', 'Mazda 2', 'Mazda 3', 'Škoda Citigo', 'Lada Niva'], 'kilometers': 100000, 'year_of_manufacture': 2009, 'wanted_counties': ['Primorsko-goranska', 'Istarska', 'Karlovačka']}

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(EncryptedType(String(length=255), os.environ.get("DB_ENCRYPTION_KEY", ""), AesEngine, "pkcs5"), nullable=False)
    search_config = Column(LONGTEXT)

    @classmethod
    def get_all(cls):
        session = session_factory()
        instance = session.query(cls).all()
        session.close()
        return instance
    
    @classmethod
    def create_user(cls, email, data=None):
        session = session_factory()
        new_user = cls(email=email, search_config=str(car_config))
        session.add(new_user)
        session.commit()
        session.close()
