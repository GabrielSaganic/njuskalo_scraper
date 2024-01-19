# coding=utf-8

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from sqlalchemy_database.common.base import Base, session_factory


class CarBrand(Base):
    __tablename__ = "car_brand"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))

    car_details = relationship("CarDetail", back_populates="car_brand")

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_or_create(cls, name):
        session = session_factory()

        instance = session.query(cls).filter_by(name=name).first()
        if instance:
            session.close()
            return instance, False

        car_brand = cls(name)
        session.add(car_brand)
        session.commit()
        instance = session.query(cls).filter_by(name=name).first()
        session.close()
        return instance, True
