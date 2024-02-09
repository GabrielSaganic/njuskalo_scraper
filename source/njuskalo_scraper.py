import logging

from bs4 import BeautifulSoup
from sqlalchemy_database.car_brand import CarBrand
from sqlalchemy_database.car_detail import CarDetail
from utils import get_car_detail, get_car_link, make_request
from s3_utilis import download_from_s3, upload_file_s3
import os

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

MIN_PRICE = 5000
MAX_PRICE = 9000
MAX_DISTANCE = 100000

list_of_active_link = []


class ScraperClass:
    def __init__(self, min_price, max_price, max_distance):
        self.min_price = min_price
        self.max_price = max_price
        self.max_distance = max_distance
        self.list_of_active_link = []
        self.next_page = True

    def start_scraping(self) -> None:
        page = 1
        while self.next_page:
            url = self.set_up_page_url(page)
            self.get_njuskalo_page(url)

            logging.info(f"Successfully get page: {page}")
            page = page + 1

        self.update_active_field()

    def get_njuskalo_page(self, url: str) -> None:
        self.next_page = False

        response = make_request(url)
        soup = BeautifulSoup(response.content, "html5lib")

        articles = soup.find_all("article", attrs={"class": "entity-body cf"})

        for article in articles:
            tmp_data = {}
            if link := get_car_link(article):
                tmp_data["link"] = link
                self.next_page = True
            else:
                continue

            self.list_of_active_link.append(link)

            if CarDetail.get_first({"link": link}):
                logging.info(f"Skipping car detail as link already exist in DB: {link}")
                continue

            response = make_request(link)
            car_detail = BeautifulSoup(response.content, "html5lib")

            tmp_data.update(get_car_detail(car_detail))

            car_brand_name = tmp_data.pop("car_brand", None)
            if not car_brand_name:
                continue

            car_brand, _ = CarBrand.get_or_create(car_brand_name)

            tmp_data["car_brand"] = car_brand
            CarDetail.get_or_create(tmp_data)
            logging.info(f"Successfully get car: {tmp_data['car_model']}")

    def set_up_page_url(self, page) -> str:
        return f"https://www.njuskalo.hr/auti?price%5Bmin%5D={self.min_price}&price%5Bmax%5D={self.max_price}&mileage%5Bmax%5D={self.max_distance}&page={page}"

    def update_active_field(self) -> None:
        CarDetail.deactivate_cars(
            self.list_of_active_link, self.min_price, self.max_price, self.max_distance
        )
        CarDetail.activate_cars(self.list_of_active_link)


def main():
    logging.info(f"Starting scraper! Good luck!")

    bucket_name = os.environ.get("BUCKET_NAME", "")
    download_from_s3("cars_detail.db", bucket_name, "tmp_cars_detail.db")

    scraper_api = ScraperClass(MIN_PRICE, MAX_PRICE, MAX_DISTANCE)
    scraper_api.start_scraping()
    
    upload_file_s3("tmp_cars_detail.db", bucket_name, "cars_detail.db")


if __name__ == "__main__":
    main()
