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

    def start_summarize_cars_job(self):
        """
        Initiates the process of summarizing top car picks and sending the summary via email.

        """
        cars_dict = self._summarize()
        self._send_email(cars_dict)

    def read_query_config(self):
        """
        Utilize this tool to adopt a more modular approach to summarizing information about cars.
        This function is designed to extract relevant details such as wanted car brand, desired countries, maximum kilometers, 
        and maximum price from a configuration file for each email recipient.
        """
        raise NotImplementedError()

    def _summarize(self) -> dict:
        """
        Summarizes the top 10 car picks based on specified criteria.
        The result is ordered by price in ascending order, and the top 10 records are
        retrieved.

        Returns:
        - dict: A dictionary containing information about the top 10 car picks, including
                car model, price, year of manufacture, kilometers, and a link.
        """
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
            .order_by(CarDetail.price.asc())
            .limit(10)
        )
        session.close()
        cars_data = read_sql(instance.statement, instance.session.bind)
        return cars_data.to_dict(orient="records")

    def _send_email(self, car_data: dict) -> None:
        """
        Sends an email containing the top 10 picks of cars to a specified recipient.
        The function uses the Simple Mail Transfer Protocol (SMTP) to send the email.

        Parameters:
        - car_data (dict): A dictionary containing information about the top 10 car picks.

        Raises:
        - Exception: If there is an error sending the email, an error message is logged.
        """
        smtp_port = 587
        smtp_server = os.environ.get("SMTP_SERVER", "")
        smtp_username = os.environ.get("SMTP_USERNAME", "")
        smtp_password = os.environ.get("APP_PASSWORD", "")

        sender_email = "gabriel.saganic@gmail.com"
        receiver_email = "gabriel.saganic@gmail.com"
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
    summarize_cars.start_summarize_cars_job()


if __name__ == "__main__":
    main()
