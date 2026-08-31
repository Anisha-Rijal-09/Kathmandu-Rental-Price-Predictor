import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import re
import time


# 
# CONFIG
# 

BASE_URL = "https://www.gharghaderi.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}

DELAY = 1.5
MAX_PAGES = 30

CATEGORIES = {
    "house-for-rent": "house",
    "flats-for-rent": "flat",
    "apartments-for-rent": "apartment"
}

CITIES = [
    "kathmandu",
    "lalitpur",
    "bhaktapur",
    "pokhara"
]


session = requests.Session()
session.headers.update(HEADERS)


# 
# BASIC HELPERS
# 

def get_text(element):
    if element:
        return element.get_text(" ", strip=True)
    return ""


def clean_text(value):
    if value is None:
        return ""

    value = str(value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# 
# PRICE
# 

def parse_price(value):
    """
    Examples:

    रु. 75,000
    रु. 1 Lakh
    रु. 1 Lakh 50 Thousand
    रु. 2 Crore
    """

    if not value:
        return None

    s = clean_text(value)

    s = (
        s.replace("रु.", "")
         .replace("रु", "")
         .replace("Rs.", "")
         .replace("Rs", "")
         .replace(",", "")
    )

    s = re.sub(
        r"per\s*month",
        "",
        s,
        flags=re.IGNORECASE
    )

    total = 0

    crore = re.search(
        r"(\d+(?:\.\d+)?)\s*crore",
        s,
        re.IGNORECASE
    )

    lakh = re.search(
        r"(\d+(?:\.\d+)?)\s*lakh",
        s,
        re.IGNORECASE
    )

    thousand = re.search(
        r"(\d+(?:\.\d+)?)\s*thousand",
        s,
        re.IGNORECASE
    )

    if crore:
        total += float(crore.group(1)) * 10000000

    if lakh:
        total += float(lakh.group(1)) * 100000

    if thousand:
        total += float(thousand.group(1)) * 1000

    # Plain number such as 75000
    if total == 0:

        numbers = re.findall(
            r"\d+(?:\.\d+)?",
            s
        )

        if numbers:
            total = float(numbers[0])

    return int(total) if total else None


# 
# AREA
# 

def parse_area_sqft(value):

    if not value:
        return None

    s = clean_text(value).lower()

    # Aana
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*aana",
        s
    )

    if match:
        return round(
            float(match.group(1)) * 342.25,
            2
        )

    # Ropani
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*ropani",
        s
    )

    if match:
        return round(
            float(match.group(1)) * 5476,
            2
        )

    # Square feet
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:sq\.?\s*ft|sqft)",
        s
    )

    if match:
        return float(match.group(1))

    return None


# 
# NUMBER EXTRACTION
# 

def first_number(value):

    if not value:
        return None

    match = re.search(
        r"\d+(?:\.\d+)?",
        str(value)
    )

    if not match:
        return None

    number = float(match.group())

    if number.is_integer():
        return int(number)

    return number


# 
# ROAD WIDTH
# 

def parse_road_width(value):

    if not value:
        return None

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*ft",
        value,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return first_number(value)


# 
# LOCATION PARSER
# 

def parse_location(location):

    result = {
        "location": "",
        "ward": "",
        "municipality": "",
        "district": "",
        "province": ""
    }

    if not location:
        return result

    location = clean_text(location)

    result["location"] = location

    # Ward

    ward_match = re.search(
        r"\b(\d{1,2})\b",
        location
    )

    if ward_match:
        result["ward"] = ward_match.group(1)

    # Municipality

    municipality_patterns = [
        r"([A-Za-z ]+ Municipality)",
        r"([A-Za-z ]+ Metropolitan City)",
        r"([A-Za-z ]+ Metropolis)",
        r"([A-Za-z ]+ Rural Municipality)"
    ]

    for pattern in municipality_patterns:

        match = re.search(
            pattern,
            location,
            re.IGNORECASE
        )

        if match:

            result["municipality"] = clean_text(
                match.group(1)
            )

            break

    # District

    districts = [
        "Kathmandu",
        "Lalitpur",
        "Bhaktapur",
        "Pokhara",
        "Kaski"
    ]

    for district in districts:

        if re.search(
            rf"\b{district}\b",
            location,
            re.IGNORECASE
        ):

            result["district"] = district
            break

    # Province

    province_match = re.search(
        r"\b(Bagmati|Gandaki|Koshi|Madhesh|Lumbini|Karnali|Sudurpashchim)\b",
        location,
        re.IGNORECASE
    )

    if province_match:
        result["province"] = province_match.group(1)

    return result


# 
# SCRAPE ONE PROPERTY
# 

def scrape_property(url):

    try:

        response = session.get(
            url,
            timeout=20
        )

    except requests.RequestException as e:

        print("Request error:", e)

        return None

    if response.status_code != 200:

        print(
            "Failed:",
            url,
            response.status_code
        )

        return None

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    data = {}

    # 
    # TITLE
    # 

    h1 = soup.select_one(
        ".first-section h1"
    )

    if h1:

        for button in h1.select("button"):
            button.decompose()

        data["title"] = get_text(h1)

    else:

        data["title"] = ""

    # 
    # PRICE / LOCATION / LAND / ROAD
    # 

    table = soup.select_one(
        ".first-section .h2 table"
    )

    if table:

        cells = table.select("td")

        if len(cells) > 0:
            data["location_raw"] = get_text(
                cells[0]
            )

        if len(cells) > 1:
            data["price_raw"] = get_text(
                cells[1]
            )

        if len(cells) > 2:
            data["land_area"] = get_text(
                cells[2]
            )

        if len(cells) > 3:
            data["road_size"] = get_text(
                cells[3]
            )

    # 
    # ALL TABLE DATA
    # 

    for table in soup.select("table"):

        rows = table.select("tr")

        for row in rows:

            cells = row.select("td")

            if len(cells) < 2:
                continue

            key = clean_text(
                get_text(cells[0])
            )

            value = clean_text(
                get_text(cells[1])
            )

            key = key.replace(
                ":",
                ""
            ).strip().lower()

            if key:

                # Don't overwrite the important
                # top-level location/price values
                if key not in data:

                    data[key] = value

    # 
    # DESCRIPTION
    # 

    desc = soup.select_one(".more")

    data["description"] = get_text(desc)

    # 
    # IMAGES
    # 

    images = []

    for a in soup.select(
        "#lightgallery a.s-slide"
    ):

        image_url = a.get("href")

        if image_url:

            image_url = urljoin(
                BASE_URL,
                image_url
            )

            if image_url not in images:
                images.append(image_url)

    data["images"] = " | ".join(images)

    data["num_images"] = len(images)

    # 
    # URL
    # 

    data["url"] = url

    return data


# 
# FIND PROPERTY LINKS
# 

def get_property_links(
    category,
    city,
    page
):

    url = (
        f"{BASE_URL}/{category}/{city}/"
        f"?page={page}"
    )

    print(
        f"Listing page: {url}"
    )

    try:

        response = session.get(
            url,
            timeout=20
        )

    except requests.RequestException as e:

        print("Request error:", e)

        return []

    if response.status_code != 200:

        print(
            "Failed:",
            response.status_code
        )

        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    links = []

    seen = set()

    for a in soup.find_all(
        "a",
        href=True
    ):

        href = a["href"]

        full_url = urljoin(
            BASE_URL,
            href
        )

        # Only property detail pages
        if not re.search(
            r"/(?:house|flat|apartment)/",
            full_url,
            re.IGNORECASE
        ):
            continue

        # Listing ID
        id_match = re.search(
            r"/(\d+)-",
            full_url
        )

        if not id_match:
            continue

        listing_id = id_match.group(1)

        if listing_id in seen:
            continue

        seen.add(listing_id)

        links.append({
            "listing_id": listing_id,
            "url": full_url,
            "category": category,
            "city": city
        })

    print(
        f"Found {len(links)} properties"
    )

    return links


# 
# FIND NUMBER OF PAGES
# 

def get_total_pages(
    category,
    city
):

    url = (
        f"{BASE_URL}/{category}/{city}/"
        f"?page=1"
    )

    try:

        response = session.get(
            url,
            timeout=20
        )

    except requests.RequestException:

        return 1

    if response.status_code != 200:
        return 1

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    text = get_text(soup)

    # Example:
    # Viewing page 1 of 3

    match = re.search(
        r"page\s+\d+\s+of\s+(\d+)",
        text,
        re.IGNORECASE
    )

    if match:

        pages = int(
            match.group(1)
        )

        return min(
            pages,
            MAX_PAGES
        )

    return 1


# 
# NORMALIZE DATA
# 

def normalize_record(
    raw,
    listing_info
):

    location_info = parse_location(
        raw.get("location_raw", "")
    )

    record = {

        "listing_id":
            listing_info["listing_id"],

        "title":
            raw.get("title", ""),

        "monthly_rent_npr":
            parse_price(
                raw.get("price_raw", "")
            ),

        "price_raw":
            raw.get("price_raw", ""),

        "land_area":
            raw.get("land_area", ""),

        "area_sqft_approx":
            parse_area_sqft(
                raw.get("land_area", "")
            ),

        "road_size":
            raw.get("road_size", ""),

        "road_width_ft":
            parse_road_width(
                raw.get("road_size", "")
            ),

        "location":
            location_info["location"],

        "ward":
            location_info["ward"],

        "municipality":
            location_info["municipality"],

        "district":
            location_info["district"],

        "province":
            location_info["province"],

        "agent_or_owner":
            raw.get("name", ""),

        "phone":
            raw.get("phone", ""),

        "email":
            raw.get("email", ""),

        "property_type":
            listing_info["category"]
                .replace(
                    "-for-rent",
                    ""
                ),

        "house_type":
            raw.get("house type", ""),

        "direction":
            raw.get("direction", ""),

        "bedrooms":
            first_number(
                raw.get("bedroom", "")
            ),

        "bathrooms":
            first_number(
                raw.get("bathroom", "")
            ),

        "living_rooms":
            first_number(
                raw.get("living room", "")
            ),

        "kitchens":
            first_number(
                raw.get("kitchen", "")
            ),

        "total_rooms":
            first_number(
                raw.get("total rooms", "")
            ),

        "parking":
            raw.get("parking", ""),

        "built_up_sqft":
            first_number(
                raw.get("built up", "")
            ),

        "no_of_flats":
            first_number(
                raw.get("no of flat", "")
            ),

        "built_year":
            raw.get("built year", ""),

        "listing_date":
            raw.get("date", ""),

        "status":
            raw.get("status", ""),

        "description":
            raw.get("description", ""),

        "images":
            raw.get("images", ""),

        "num_images":
            raw.get("num_images", 0),

        "city":
            listing_info["city"],

        "url":
            listing_info["url"],

        "source":
            "gharghaderi.com"
    }

    return record


# 
# MAIN SCRAPER
# 

def main():

    print("=" * 70)
    print("GHARGHADERI NEPAL RENTAL DATASET SCRAPER")
    print("=" * 70)

    all_links = []

    # 
    # STEP 1
    # GET ALL PROPERTY URLS
    # 

    for category, property_type in CATEGORIES.items():

        for city in CITIES:

            print(
                f"\n### {property_type.upper()} - "
                f"{city.upper()} ###"
            )

            total_pages = get_total_pages(
                category,
                city
            )

            print(
                f"Total pages: {total_pages}"
            )

            for page in range(
                1,
                total_pages + 1
            ):

                links = get_property_links(
                    category,
                    city,
                    page
                )

                all_links.extend(
                    links
                )

                time.sleep(
                    DELAY
                )

    # 
    # DEDUPLICATE
    # 

    unique_links = {}

    for item in all_links:

        unique_links[
            item["listing_id"]
        ] = item

    all_links = list(
        unique_links.values()
    )

    print("\n" + "=" * 70)

    print(
        f"TOTAL UNIQUE PROPERTIES: "
        f"{len(all_links)}"
    )

    print("=" * 70)

    # 
    # STEP 2
    # SCRAPE EACH PROPERTY
    # 

    records = []

    for index, item in enumerate(
        all_links,
        start=1
    ):

        print(
            f"\n[{index}/{len(all_links)}] "
            f"ID: {item['listing_id']}"
        )

        raw_data = scrape_property(
            item["url"]
        )

        if raw_data:

            record = normalize_record(
                raw_data,
                item
            )

            records.append(
                record
            )

        time.sleep(
            DELAY
        )

    # 
    # DATAFRAME
    # 

    df = pd.DataFrame(records)

    # Remove duplicates
    if not df.empty:

        df.drop_duplicates(
            subset=["listing_id"],
            inplace=True
        )

    # 
    # SAVE
    # 

    output_file = (
        "nepal_rental_dataset.csv"
    )

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    # 
    # SUMMARY
    # 

    print("\n")
    print("=" * 70)
    print("SCRAPING FINISHED")
    print("=" * 70)

    print(
        f"Records: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print(
        f"Saved to: {output_file}"
    )

    print("\nColumns:")

    for column in df.columns:
        print(
            f"  {column}"
        )

    print("\nMissing values:")

    print(
        df.isnull().sum()
    )


# 
# RUN
# 

if __name__ == "__main__":
    main()