from bs4 import BeautifulSoup
import sys
from sqlalchemy_database.car_brand import CarBrand
from sqlalchemy_database.car_detail import CarDetail 


from utils import (
    read_from_file,
    get_car_link,
    get_car_company,
    make_request,
)

MIN_PRICE = 3000
MAX_PRICE = 5000
MAX_DISTANCE = 200000

URL = f"https://www.njuskalo.hr/auti?price%5Bmin%5D={MIN_PRICE}&price%5Bmax%5D={MAX_PRICE}&mileage%5Bmax%5D={MAX_DISTANCE}"


if __name__ == "__main__":
    debug = False
    try:
        if sys.argv[1] == "--test":
            debug = True
    except:
        pass

    if debug:
        response = read_from_file("car_list_example_html.txt")
        soup = BeautifulSoup(response, "html5lib")
    else:
        response = make_request(URL)
        soup = BeautifulSoup(response.content, "html5lib")

        # with open("car_list_example_html.txt", "wb") as file:
        #     file.write(response.content)

    articles = soup.find_all("article", attrs={"class": "entity-body cf"})

    for article in articles:
        tmp_data = {}
        if link := get_car_link(article):
            tmp_data["link"] = link
        else:
            continue

        if "https://www.njuskalo.hr/auti/" not in link:
            continue

        if debug:
            response = read_from_file("car_detail_example_html.txt")
            car_detail = BeautifulSoup(response, "html5lib")
        else:
            response = make_request(link)
            car_detail = BeautifulSoup(response.content, "html5lib")

            # with open("car_detail_example_html.txt", "wb") as file:
            #     file.write(response.content)

        tmp_data.update(get_car_company(car_detail))

        car_brand_name = tmp_data.pop("car_brand")
        car_brand, _ = CarBrand.get_or_create(car_brand_name)

        tmp_data["car_brand"] = car_brand
        CarDetail.get_or_create(tmp_data)

