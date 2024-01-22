import logging
import secrets
import os
from urllib.parse import urljoin

import requests


def try_except_decorator(default_value):
    def decorator(original_function):
        def wrapped_function(*args, **kwargs):
            try:
                result = original_function(*args, **kwargs)
                return result
            except Exception as e:
                logging.error(
                    f"An exception occurred in {original_function.__name__}: {e}"
                )
                return default_value

        return wrapped_function

    return decorator


def get_headers(url: str) -> None:
    return {
        "Host": "www.njuskalo.hr",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/vnd.api+json",
        "Authorization": generate_bearer_token(),
        "Connection": "keep-alive",
        "Referer": url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }


@try_except_decorator("")
def get_car_link(article) -> str:
    h3_tag_title = article.find("h3", attrs={"class": "entity-title"})
    if h3_tag_title:
        a_tag = h3_tag_title.find("a", attrs={"class": "link"})
        link = a_tag.get("href")
        link = urljoin("https://www.njuskalo.hr", link)
        if "https://www.njuskalo.hr/auti/" in link:
            return link
    return ""


@try_except_decorator(None)
def make_request(url: str) -> None:
    response = requests.get(url=url, headers=get_headers(url))
    response.raise_for_status()
    return response


@try_except_decorator("")
def read_from_file(file: str) -> None:
    with open(file, "r") as file:
        content = file.read()
    return content


EXPECTED_DETAILS = {
    "Lokacija vozila",
    "Marka automobila",
    "Model automobila",
    "Tip automobila",
    "Godina proizvodnje",
    "Registriran do",
    "Prijeđeni kilometri",
    "Motor",
    "Snaga motora",
    "Radni obujam",
    "Potrošnja goriva",
}

FIELD_MAPPING = {
    "Lokacija vozila": "location",
    "Marka automobila": "car_brand",
    "Model automobila": "car_model",
    "Tip automobila": "type_of_car",
    "Godina proizvodnje": "year_of_manufacture",
    "Registriran do": "registered_until",
    "Prijeđeni kilometri": "kilometers",
    "Motor": "engine",
    "Snaga motora": "engine_power",
    "Radni obujam": "work_volume",
    "Potrošnja goriva": "fuel_consumption",
}


@try_except_decorator("")
def clear_text(text: str) -> str:
    return (
        text.replace(". godište", "")
        .replace(" km", "")
        .replace(" kW", "")
        .replace(" cm3", "")
        .replace(" l/100km", "")
        .replace("\xa0€", "")
    )


@try_except_decorator({})
def get_car_detail(detail) -> dict:
    tmp_dict = {}
    basic_details = detail.find_all(
        "span", attrs={"class": "ClassifiedDetailBasicDetails-textWrapContainer"}
    )
    for index, basic_detail in enumerate(basic_details):
        if basic_detail.text in EXPECTED_DETAILS:
            tmp_dict[FIELD_MAPPING.get(basic_detail.text)] = clear_text(
                basic_details[index + 1].text
            )

    price_tag = detail.find(
        "span", attrs={"class": "ClassifiedDetailCreditCalculator-totalAmountPriceBit"}
    )
    tmp_dict["price"] = clear_text(price_tag.text)
    return tmp_dict


@try_except_decorator("")
def generate_email_html(car_data: dict) -> None:
    with open("source/email_template/daily_summarize.html", "r") as file:
        html = file.read()

    table_rows = ""
    for car in car_data:
        table_rows += f"""
            <tr>
                <td>{car['car_model']}</td>
                <td>{car['price']}</td>
                <td>{car['year_of_manufacture']}</td>
                <td>{car['kilometers']}</td>
                <td><a href="{car['link']}">View Details</a></td>
            </tr>
        """
    return html.replace("[TABLE_ROWS]", table_rows)


@try_except_decorator("")
def generate_email_text(car_data: dict) -> None:
    text = """
        Hi there,

        We hope this message finds you well.

        As part of our commitment to keeping you informed about the latest and greatest in the automotive world, we're thrilled to present your personalized list of the top 10 best available cars for today! 
        """
    return f"{text}\n{car_data}"

@try_except_decorator("")
def generate_bearer_token() -> str:
    bearer_token = secrets.token_urlsafe(656)
    return f"Bearer {bearer_token}"
