"""
Nepal Rental Price Dataset Scraper
Source: gharghaderi.com (public listing pages, no login required)

Run this on your own machine or in Google Colab:
    pip install requests beautifulsoup4 pandas
    python scrape_gharghaderi.py

Output: nepal_rental_dataset.csv

Be a good citizen while scraping:
- We add a delay between requests (time.sleep)
- We only hit public listing pages (no login, no personal data)
- Keep this to ONE crawl; don't run it repeatedly / on a loop
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import csv

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# category -> (url_slug, property_type_label)
CATEGORIES = {
    "house-for-rent": "house",
    "flats-for-rent": "flat",
    "apartments-for-rent": "apartment",
}

CITIES = ["kathmandu", "lalitpur", "bhaktapur", "pokhara"]


def parse_price(price_str):
    """Convert Nepali price text like 'रु. 1 Lakh 50 Thousand Per Month' to numeric NPR."""
    if not price_str:
        return None
    s = price_str.replace("रु.", "").replace("Rs.", "")
    s = re.sub(r'per\s*month', '', s, flags=re.IGNORECASE)
    total = 0
    m = re.search(r'(\d+(?:\.\d+)?)\s*Crore', s, re.IGNORECASE)
    if m:
        total += float(m.group(1)) * 1_00_00_000
    m = re.search(r'(\d+(?:\.\d+)?)\s*Lakh', s, re.IGNORECASE)
    if m:
        total += float(m.group(1)) * 1_00_000
    m = re.search(r'(\d+(?:\.\d+)?)\s*Thousand', s, re.IGNORECASE)
    if m:
        total += float(m.group(1)) * 1_000
    if total == 0:
        digits = re.sub(r'[^\d]', '', s)
        if digits:
            total = int(digits)
    return int(total) if total else None


def parse_area_sqft(area_str):
    """Convert aana/ropani/sqft text to approx sqft."""
    if not area_str:
        return None
    m = re.search(r'(\d+(?:\.\d+)?)\s*aana', area_str, re.IGNORECASE)
    if m:
        return round(float(m.group(1)) * 342.25, 1)
    m = re.search(r'(\d+(?:\.\d+)?)\s*ropani', area_str, re.IGNORECASE)
    if m:
        return round(float(m.group(1)) * 5476, 1)
    m = re.search(r'(\d+(?:\.\d+)?)\s*(sq\.?\s*ft|sqft)', area_str, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def scrape_page(url):
    """Scrape one listing page, return a list of dicts."""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")

    records = []
    # Each listing is an <a> tag linking to /house/, /flat/, /apartment/, /office/, /land/
    listing_links = soup.select('a[href*="/house/"], a[href*="/flat/"], a[href*="/apartment/"]')

    seen = set()
    for a in listing_links:
        href = a.get("href")
        if not href or href in seen:
            continue
        seen.add(href)
        text = a.get_text(" ", strip=True)
        if not text or "rent" not in text.lower():
            continue

        # Extract listing ID
        id_match = re.search(r'ID\s*(\d+)', text)
        listing_id = id_match.group(1) if id_match else None

        # Extract price
        price_match = re.search(r'रु\.?\s*[\d,]*\s*(?:Crore)?\s*[\d,]*\s*(?:Lakh)?\s*[\d,]*\s*(?:Thousand)?[\d,]*', text)
        price_raw = price_match.group(0) if price_match else None

        # Extract road width
        road_match = re.search(r'(\d+(?:\.\d+)?)\s*ft\s*Road', text)
        road_width = float(road_match.group(1)) if road_match else None

        # Extract area (aana/ropani)
        area_match = re.search(r'(\d+(?:\.\d+)?\s*(?:aana|ropani))', text, re.IGNORECASE)
        area_raw = area_match.group(1) if area_match else None

        records.append({
            "listing_id": listing_id,
            "url": href if href.startswith("http") else f"https://www.gharghaderi.com{href}",
            "raw_text": text,
            "monthly_rent_npr": parse_price(price_raw) if price_raw else None,
            "area_raw": area_raw,
            "area_sqft_approx": parse_area_sqft(area_raw) if area_raw else None,
            "road_width_ft": road_width,
        })
    return records


def get_total_pages(soup_or_url):
    """Best-effort: try page=1..30 until a page returns no new listings."""
    return 30  # upper bound safety; loop below breaks early when empty


def main():
    all_rows = []
    for slug, ptype in CATEGORIES.items():
        for city in CITIES:
            page = 1
            empty_streak = 0
            while page <= 30 and empty_streak < 2:
                url = f"https://www.gharghaderi.com/{slug}/{city}/?page={page}"
                print(f"Scraping {url} ...")
                try:
                    records = scrape_page(url)
                except Exception as e:
                    print(f"  error: {e}")
                    break
                if not records:
                    empty_streak += 1
                else:
                    empty_streak = 0
                    for r in records:
                        r["property_type"] = ptype
                        r["city"] = city
                        r["source"] = "gharghaderi.com"
                    all_rows.extend(records)
                page += 1
                time.sleep(1.5)  # be polite

    # De-duplicate by listing_id
    seen_ids = set()
    deduped = []
    for r in all_rows:
        key = r.get("listing_id") or r.get("url")
        if key in seen_ids:
            continue
        seen_ids.add(key)
        deduped.append(r)

    fieldnames = ["listing_id", "city", "property_type", "monthly_rent_npr",
                  "area_raw", "area_sqft_approx", "road_width_ft",
                  "raw_text", "url", "source"]

    with open("nepal_rental_dataset.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped)

    print(f"\nDone. Wrote {len(deduped)} unique listings to nepal_rental_dataset.csv")


if __name__ == "__main__":
    main()
