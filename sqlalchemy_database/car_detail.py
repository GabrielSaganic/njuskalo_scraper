# coding=utf-8

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from sqlalchemy_database.common.base import Base, session_factory


class CarDetail(Base):
    __tablename__ = "car_detail"

    id = Column(Integer, primary_key=True)
    car_brand_id = Column(Integer, ForeignKey("car_brand.id"))
    price = Column(Integer)
    location = Column(String(length=255), nullable=True)
    car_model = Column(String(length=255))
    type_of_car = Column(String(length=255), nullable=True)
    year_of_manufacture = Column(Integer)
    registered_until = Column(String(length=255), nullable=True)
    kilometers = Column(Integer)
    engine = Column(String(length=255), nullable=True)
    engine_power = Column(Integer, nullable=True)
    work_volume = Column(Float, nullable=True)
    fuel_consumption = Column(Float, nullable=True)
    link = Column(String(length=255))
    created_at = Column(DateTime(timezone=True), default=func.now())
    fuel_consumption = Column(Float, nullable=True)
    active = Column(Boolean, default=True)

    car_brand = relationship("CarBrand", back_populates="car_details")

    def __init__(
        self,
        car_brand,
        price,
        link,
        car_model,
        year_of_manufacture,
        kilometers,
        location=None,
        type_of_car=None,
        registered_until=None,
        engine=None,
        engine_power=None,
        work_volume=None,
        fuel_consumption=None,
    ):
        self.car_brand = car_brand
        self.price = price
        self.location = location
        self.car_model = car_model
        self.type_of_car = type_of_car
        self.year_of_manufacture = year_of_manufacture
        self.registered_until = registered_until
        self.kilometers = kilometers
        self.engine = engine
        self.engine_power = engine_power
        self.work_volume = work_volume
        self.fuel_consumption = fuel_consumption
        self.link = link

    @classmethod
    def get_or_create(cls, data: dict):
        session = session_factory()

        instance = session.query(cls).filter_by(**data).first()
        if instance:
            session.close()
            return instance, False

        car_detail = cls(**data)
        session.add(car_detail)
        session.commit()
        instance = session.query(cls).filter_by(**data).first()
        session.close()
        return instance, True

    @classmethod
    def get_first(cls, data: dict):
        session = session_factory()
        instance = session.query(cls).filter_by(**data).first()
        session.close()
        return instance
    
    @classmethod
    def deactivate_cars(cls, list_of_active_link, min_price, max_price, max_distance):
        session = session_factory()

        session.query(cls).filter(
            ~cls.link.in_(list_of_active_link),
        ).update({"active": False}, synchronize_session=False)

        session.commit()
        session.close()

    @classmethod
    def activate_cars(cls, list_of_active_link):
        session = session_factory()

        session.query(cls).filter(
            cls.link.in_(list_of_active_link),
        ).update({"active": True}, synchronize_session=False)

        session.commit()
        session.close()
