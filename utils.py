import requests
from urllib.parse import urljoin


def get_headers(url):
    return {
        "Host": "www.njuskalo.hr",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/vnd.api+json",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJuanVza2Fsb19qc19hcHAiLCJqdGkiOiIyYjhmZGU0Yzk5ZjFjNTRkNGM1NWExNDA0ZGUzODUxYTI5MWMyYTU3N2I2YmZmMTJjOTJhMjM5MGYwOTM0NTcyZGE2MjUzZTY5YTQ5MzYzZSIsImlhdCI6MTcwNTM0NzIwMS43ODkyMTQsIm5iZiI6MTcwNTM0NzIwMS43ODkyMTUsImV4cCI6MTcwNTM2ODgwMS43ODU2MzMsInN1YiI6IiIsInNjb3BlcyI6W119.UaEQyo9Nn0pTXONY2lBE_eJGEolJ0TReBZ7LS3PJXqseGIesciPIoOjasTRSWQQfQRDcZEOfSk7t3r_CpiR671ajDbL9EzZCaPVqRsWb1rrP-6_dY4PNa86_e_qhU2xUascHHi3pbUwnS9FRpdF6r1NC6A5LAsBRtjDtj1aIuGR7zZ75j_x-47nXrIo0SKPccp1cSCIAdJA8lRRjuSJEdAgjmXzWcgQHErqMnSRxewA4jKBa54PbHUyW92tkNmkfiMSw18jopdXnX81fS5rFZqVCRj-wWoNH6fZQJuSFxsDC4_DD1CLbxGFZsQRap3FU5IesWP0BWww7qIAIytFd1Q",
        "Connection": "keep-alive",
        "Referer": url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }


def get_car_link(article) -> str:
    h3_tag_title = article.find("h3", attrs={"class": "entity-title"})
    if h3_tag_title:
        a_tag = h3_tag_title.find("a", attrs={"class": "link"})
        link = a_tag.get("href")
        return urljoin("https://www.njuskalo.hr", link)
    return ""


def make_request(url):
    return requests.get(url=url, headers=get_headers(url))


def read_from_file(file):
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

def clear_text(text: str) -> str:
    return (
        text.replace(". godište", "")
        .replace(" km", "")
        .replace(" kW", "")
        .replace(" cm3", "")
        .replace(" l/100km", "")
    )


def get_car_company(detail) -> str:
    tmp_dict = {}
    basic_details = detail.find_all(
        "span", attrs={"class": "ClassifiedDetailBasicDetails-textWrapContainer"}
    )
    for index, basic_detail in enumerate(basic_details):
        if basic_detail.text in EXPECTED_DETAILS:
            tmp_dict[FIELD_MAPPING.get(basic_detail.text)] = clear_text(basic_details[index + 1].text)
    return tmp_dict
