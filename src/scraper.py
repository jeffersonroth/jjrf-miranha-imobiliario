"""McMakler's Web Scraper"""

import sys
import re
from time import sleep

from selenium.webdriver.common.by import By
from utils.selenium_hub import get_web_driver
from utils.mongo import get_client, setup_db

# URLs
URL_BASE = "https://www.mcmakler.de"


def get_pages(url: str, wait_until_id: list):
    """Gets the number of pages."""
    html = get_web_driver(url=url, wait_until_id=wait_until_id)
    pages = [li.find("a").text for li in html.find_all("li")]
    last_page = 1
    for page in pages:
        try:
            last_page = int(page) if int(page) > last_page else last_page
        except ValueError:
            last_page = last_page
    return last_page


def get_house_attributes(dl) -> dict:
    """Gets house attributes from dl elements."""
    attrs = {el.find("p").text: dd.text for el in dl for dd in el.find("dd")}
    print(f"Attributes: {attrs}", file=sys.stdout)
    return attrs


def states_collection(url: str = f"{URL_BASE}/immobilien/"):
    """Scrapes URL and retrieve list of States (Ländern) URLs."""
    html = get_web_driver(url)
    regexp = re.compile(r"^/immobilien/")
    elements = html.find_all("a", {"href": regexp})
    collection = get_client()["mcmakler"]["states"]
    for el in elements:
        state = el.get_text()
        href = el.get("href")
        entry = {
            "state": state,
            "url": href
        }
        print(f"[mcmakler.states] Inserting {state}", file=sys.stdout)
        collection.update_one({"url": href}, {"$set": entry}, upsert=True)


def cities_collection():
    """Scrapes URL and retrieve list of cities URLs."""
    collection = get_client()["mcmakler"]["cities"]
    states_cursor = get_client()["mcmakler"]["states"].find(no_cursor_timeout=True)
    for s in states_cursor:
        url = f"{URL_BASE}{s['url']}"
        state = s["state"]
        print(f"Retrieving data for {state} state [{url}]", file=sys.stdout)
        html = get_web_driver(url)
        regexp = re.compile(f"{s['url']}/")
        elements = html.find_all("a", {"href": regexp})
        for el in elements:
            city = el.get_text()
            href = el.get("href")
            entry = {
                "state": state,
                "city": city,
                "url": href
            }
            print(f"[mcmakler.cities] Inserting {state} / {city}", file=sys.stdout)
            collection.update_one({"url": href}, {"$set": entry}, upsert=True)
    states_cursor.close()


def houses_collection():
    """Scrapes URL and retrieve list of houses URLs."""
    collection = get_client()["mcmakler"]["houses"]
    cities_cursor = get_client()["mcmakler"]["cities"].find(no_cursor_timeout=True)
    for c in cities_cursor:
        url = f"{URL_BASE}{c['url']}"
        state = c["state"]
        city = c["city"]
        last_page = get_pages(url=url, wait_until_id=[By.CLASS_NAME, "pagination"])

        for page in range(last_page):
            print(f"Retrieving data for {state} / {city} [{url}] [Page {page + 1} of {last_page}]", file=sys.stdout)
            page_url = f"{URL_BASE}{c['url']}?page={page}"
            html = get_web_driver(url=page_url, wait_until_id=[By.CLASS_NAME, "css-gdcr9g"])
            regexp = re.compile(r"/immobilien/expose/")
            elements = html.find_all("a", {"href": regexp})

            for el in elements:
                href = el.get("href")
                entry = {
                    "state": state,
                    "city": city,
                    "url": href,
                    "object_type": None,  # Objekttyp (Object type)
                    "living_space": 0.00,  # Wohnfläche (Living space)
                    "purchase_price": 0.00,  # Kaufpreis (Purchase price)
                    "purchase_price_sqm": 0.00,  # Kaufpreis pro qm (Purchase price per sqm)
                    "available_from": None,  # Verfügbar ab (Available from)
                    "house_url": f"{URL_BASE}{href}"
                }
                print(f"[mcmakler.houses] Inserting {href} for {state} / {city}", file=sys.stdout)
                collection.update_one({"url": href}, {"$set": entry}, upsert=True)

        houses_cursor = collection.find({"state": state, "city": city}, no_cursor_timeout=True)
        for h in houses_cursor:
            url = h["house_url"]
            house = h["url"].split("/immobilien/expose/")[1].replace("/", "").strip()
            print(f"[mcmakler.houses] Updating {state} / {city} / {house} [{URL_BASE}{h['url']}]", file=sys.stdout)
            html = get_web_driver(url=url, wait_until_id=[By.CLASS_NAME, "css-es6bjo"])
            attrs = get_house_attributes(dl=html.find_all("dl", {"class": re.compile(r"css-nr29fk")}))
            for key, value in attrs.items():
                if key == "Objekttyp":
                    v = value.strip().upper()
                    print(f"{house}.object_type (Objekttyp): {v}", file=sys.stdout)
                    collection.update_one(
                        {"url": h["url"]},
                        {"$set": {"object_type": v}},
                        upsert=True
                    )
                if key == "Wohnfläche":
                    try:
                        v = float(
                            value.replace("m2", "")
                                .replace(".", "")
                                .replace(",", ".")
                                .strip()
                        )
                        print(f"{house}.living_space (Wohnfläche): {v}", file=sys.stdout)
                        collection.update_one(
                            {"url": h["url"]},
                            {"$set": {"living_space": v}},
                            upsert=True
                        )
                    except ValueError:
                        print(f"Could not parse '{value}' as float", file=sys.stdout)
                        pass
                if key == "Kaufpreis":
                    try:
                        v = float(
                            value.replace("\xa0€", "")
                                .replace("\xa0", "")
                                .replace("€", "")
                                .replace(".", "")
                                .replace(",", ".")
                                .strip()
                        )
                        print(f"{house}.purchase_price (Kaufpreis): {v}", file=sys.stdout)
                        collection.update_one(
                            {"url": h["url"]},
                            {"$set": {"purchase_price": v}},
                            upsert=True
                        )
                    except ValueError:
                        print(f"Could not parse '{value}' as float", file=sys.stdout)
                        pass
                if key == "Kaufpreis pro qm":
                    try:
                        v = float(
                            value.replace("\xa0€", "")
                                .replace("\xa0", "")
                                .replace("€", "")
                                .replace(".", "")
                                .replace(",", ".")
                                .strip()
                        )
                        print(f"{house}.purchase_price_sqm (Kaufpreis pro qm): {v}", file=sys.stdout)
                        collection.update_one(
                            {"url": h["url"]},
                            {"$set": {"purchase_price_sqm": v}},
                            upsert=True
                        )
                    except ValueError:
                        print(f"Could not parse '{value}' as float", file=sys.stdout)
                        pass
        houses_cursor.close()
    cities_cursor.close()


if __name__ == "__main__":
    setup_db()
    sleep(15)
    states_collection()
    cities_collection()
    houses_collection()
