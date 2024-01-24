import logging

from sqlalchemy_database.user import User
from utils import mask_email

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

search_config = {
    "car_model": [
        "Toyota Yaris",
        "Toyota Aygo",
        "Toyota iQ",
        "Ford Fiesta",
        "Ford Focus",
        "Ford Ka",
        "Ford Fusion",
        "VW Polo",
        "VW Up!",
        "VW Golf 6",
        "VW Golf 5",
        "VW Golf 4",
        "VW Fox",
        "Fiat Punto",
        "Fiat 500",
        "Renault Twingo",
        "Renault 5",
        "Renault Clio",
        "Renault 4",
        "Peugeot 107",
        "Peugeot 208",
        "Peugeot 207",
        "Peugeot 205",
        "Peugeot 108",
        "Peugeot 307",
        "Hyundai i10",
        "Hyundai i20",
        "Citroën C1",
        "Citroën C3",
        "Citroën C2",
        "Opel Corsa",
        "Seat Ibiza",
        "Seat Leon",
        "Seat Mii",
        "Seat Altea",
        "Nissan Note",
        "Nissan Micra",
        "Suzuki Celerio",
        "Suzuki Alto",
        "Kia Picanto",
        "Kia Venga",
        "Mazda 2",
        "Mazda 3",
        "Škoda Citigo",
        "Lada Niva",
    ],
    "kilometers": 100000,
    "year_of_manufacture": 2009,
    "wanted_counties": ["Primorsko-goranska", "Istarska", "Karlovačka"],
}


try:
    email = "exampel.example@gmail.com"
    User.create_user(email, str(search_config))
    logging.info(f"Successfully added user: {mask_email(email)}")
except Exception as e:
    logging.error(f"Error adding user: {mask_email(email)}. Detail: {e}")
