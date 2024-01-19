import logging
import sys

from bs4 import BeautifulSoup

from sqlalchemy_database.car_brand import CarBrand
from sqlalchemy_database.car_detail import CarDetail
from utils import get_car_detail, get_car_link, make_request, read_from_file

MIN_PRICE = 3000
MAX_PRICE = 3200
MAX_DISTANCE = 150000

list_of_active_link = []

def get_njuskalo_page(url: str, safe_next_page: int, debug: bool = False):
    next_page = False
    if debug:
        response = read_from_file("car_list_example_html.txt")
        soup = BeautifulSoup(response, "html5lib")
    else:
        response = make_request(url)
        soup = BeautifulSoup(response.content, "html5lib")

        # with open("car_list_example_html.txt", "wb") as file:
        #     file.write(response.content)

    articles = soup.find_all("article", attrs={"class": "entity-body cf"})
    if not articles:
        next_page = False

    for article in articles:
        tmp_data = {}
        if link := get_car_link(article):
            tmp_data["link"] = link
            next_page = True
        else:
            continue
        
        if link == "https://www.njuskalo.hr/auti/renault-twingo-1.2-2009-god-150000-km-servo-kartice-oglas-42072374" or link == "https://www.njuskalo.hr/auti/peugeot-308-1.4-16v-vti-oglas-42464154":
            pass
        else:
            list_of_active_link.append(link)
            pass
        # list_of_active_link.append(link)
        
        if CarDetail.get_first({"link": link}):
            logging.info(f"Skipping car detail as link already exist in DB: {link}")
            continue


        if debug:
            response = read_from_file("car_detail_example_html.txt")
            car_detail = BeautifulSoup(response, "html5lib")
        else:
            response = make_request(link)
            car_detail = BeautifulSoup(response.content, "html5lib")

            # with open("car_detail_example_html.txt", "wb") as file:
            #     file.write(response.content)

        tmp_data.update(get_car_detail(car_detail))

        car_brand_name = tmp_data.pop("car_brand", None)
        if not car_brand_name:
            continue

        car_brand, _ = CarBrand.get_or_create(car_brand_name)

        tmp_data["car_brand"] = car_brand
        CarDetail.get_or_create(tmp_data)
        safe_next_page = 5
        logging.info(f"Successfully get car: {tmp_data['car_model']}")

    return next_page, safe_next_page - 1


def set_up_page_url(page):
    return f"https://www.njuskalo.hr/auti?price%5Bmin%5D={MIN_PRICE}&price%5Bmax%5D={MAX_PRICE}&mileage%5Bmax%5D={MAX_DISTANCE}&page={page}"

def update_non_active_record():
    CarDetail.deactivate_cars(list_of_active_link, MIN_PRICE, MAX_PRICE, MAX_DISTANCE)
    CarDetail.activate_cars(list_of_active_link)

def main():
    logging.info(f"Starting scraper! Good luck!")

    debug = False
    try:
        if sys.argv[1] == "--test":
            debug = True
    except:
        pass

    page = 1
    next_page = True
    safe_next_page = 5
    while next_page and safe_next_page > 0:
        next_page, safe_next_page = get_njuskalo_page(
            set_up_page_url(page), safe_next_page, debug
        )
        logging.info(f"Successfully get page: {page}")
        page = page + 1

    update_non_active_record()

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    main()
