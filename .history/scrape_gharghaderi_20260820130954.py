import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time


BASE_URL = "https://www.gharghaderi.com"


def get_text(element):
    if element:
        return element.get_text(" ", strip=True)
    return ""


def scrape_property(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/151.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200:
        print("Failed:", url, response.status_code)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    data = {}

    # ------------------------------------------------
    # TITLE
    # ------------------------------------------------

    h1 = soup.select_one(".first-section h1")

    if h1:
        # Remove buttons from title
        for button in h1.select("button"):
            button.decompose()

        data["title"] = h1.get_text(" ", strip=True)
    else:
        data["title"] = ""

    # ------------------------------------------------
    # PRICE / LOCATION / LAND / ROAD
    # ------------------------------------------------

    table = soup.select_one(".first-section .h2 table")

    if table:

        cells = table.select("td")

        # Location
        if len(cells) > 0:
            data["location"] = get_text(cells[0])

        # Price
        if len(cells) > 1:
            data["price"] = get_text(cells[1])

        # Land
        if len(cells) > 2:
            data["land_area"] = get_text(cells[2])

        # Road
        if len(cells) > 3:
            data["road_size"] = get_text(cells[3])

    # ------------------------------------------------
    # OWNER / BASIC INFORMATION
    # ------------------------------------------------

    owner_table = None

    for table in soup.select("table"):
        text = get_text(table)

        if "Listing ID" in text and "Status" in text:
            owner_table = table
            break

    if owner_table:

        rows = owner_table.select("tr")

        for row in rows:

            cells = row.select("td")

            if len(cells) >= 2:

                key = get_text(cells[0])
                value = get_text(cells[1])

                key = key.replace(":", "").strip().lower()

                if key:
                    data[key] = value

    # ------------------------------------------------
    # PROPERTY DETAILS
    # ------------------------------------------------

    # Find table containing "Land area" / "House type"
    for table in soup.select("table"):

        text = get_text(table)

        if "House type" in text or "Land area" in text:

            rows = table.select("tr")

            for row in rows:

                cells = row.select("td")

                if len(cells) >= 2:

                    key = get_text(cells[0])
                    value = get_text(cells[1])

                    key = key.replace(":", "").strip().lower()

                    if key:
                        data[key] = value

    # ------------------------------------------------
    # INTERIOR FEATURES
    # ------------------------------------------------

    for table in soup.select("table"):

        text = get_text(table)

        if "Bedroom" in text or "Living Room" in text:

            rows = table.select("tr")

            for row in rows:

                cells = row.select("td")

                if len(cells) >= 2:

                    key = get_text(cells[0])
                    value = get_text(cells[1])

                    key = key.replace(":", "").strip().lower()

                    if key:
                        data[key] = value

    # ------------------------------------------------
    # PROPERTY DESCRIPTION
    # ------------------------------------------------

    desc = soup.select_one(".more")

    data["description"] = get_text(desc)

    # ------------------------------------------------
    # IMAGES
    # ------------------------------------------------

    images = []

    for a in soup.select("#lightgallery a.s-slide"):

        image_url = a.get("href")

        if image_url:

            image_url = urljoin(BASE_URL, image_url)

            if image_url not in images:
                images.append(image_url)

    data["images"] = " | ".join(images)

    # Number of images
    data["num_images"] = len(images)

    # ------------------------------------------------
    # URL
    # ------------------------------------------------

    data["url"] = url

    return data


# ------------------------------------------------
# TEST WITH ONE PROPERTY
# ------------------------------------------------

url = "https://www.gharghaderi.com/house/9541-House-for-rent/"

property_data = scrape_property(url)

print(property_data)