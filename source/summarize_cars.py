import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pandas import read_sql
from sqlalchemy import or_
from sqlalchemy_database.car_brand import CarBrand
from sqlalchemy_database.car_detail import CarDetail
from sqlalchemy_database.common.base import session_factory
from utils import generate_email_html, generate_email_text

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


class SummarizeCars:
    def __init__(self):
        self.wanted_car_brand = [
            "Toyota",
            "Ford",
            "VW",
            "Fiat",
            "Renault",
            "Peugeot",
            "Citroën",
            "Hyundai",
            "Opel",
            "Seat",
            "Nissan",
            "Suzuki",
            "Kia",
            "Mazda",
            "Škoda",
            "Honda",
            "Lada",
        ]
        self.wanted_counties = ["Primorsko-goranska", "Istarska", "Karlovačka"]

    def summarize(self):
        session = session_factory()
        instance = (
            session.query(
                (CarBrand.name + " " + CarDetail.car_model).label("car_model"),
                CarDetail.price,
                CarDetail.year_of_manufacture,
                CarDetail.kilometers,
                CarDetail.link,
            )
            .join(CarBrand)
            .filter(
                CarBrand.name.in_(self.wanted_car_brand),
                or_(
                    *[
                        CarDetail.location.ilike(f"%{county}%")
                        for county in self.wanted_counties
                    ]
                ),
                CarDetail.kilometers < 100000,
                CarDetail.active == True,
            )
        )
        session.close()
        cars_data = read_sql(instance.statement, instance.session.bind)
        self.send_email(cars_data.to_dict(orient="records"))

    def send_email(self, car_data):
        smtp_port = 587
        smtp_server = os.environ.get("SMTP_SERVER", "")
        smtp_username = os.environ.get("SMTP_USERNAME", "")
        smtp_password = os.environ.get("APP_PASSWORD", "")

        sender_email = "mailtrap@example.com"
        receiver_email = "new@example.com"
        message = MIMEMultipart("alternative")
        message[
            "Subject"
        ] = "Your Daily Top 10 Picks: The Finest Cars on the Market Today!"
        message["From"] = sender_email
        message["To"] = receiver_email

        html = generate_email_html(car_data)
        text = generate_email_text(car_data)

        # convert both parts to MIMEText objects and add them to the MIMEMultipart message
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        try:
            # send your email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, receiver_email, message.as_string())

            logging.info("Email sent!")
        except Exception as e:
            logging.error(f"Error sending email! Detail: {e}.")


def main():
    logging.info("Starting summarizing!")
    summarize_cars = SummarizeCars()
    summarize_cars.summarize()


if __name__ == "__main__":
    main()
