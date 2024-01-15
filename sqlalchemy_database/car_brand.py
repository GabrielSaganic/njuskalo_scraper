# coding=utf-8

from sqlalchemy import Column, String, Integer

from sqlalchemy_database.common.base import Base, session_factory
from sqlalchemy.orm import relationship


class CarBrand(Base):
    __tablename__ = "car_brand"

    id = Column(Integer, primary_key=True)
    name = Column(String)

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