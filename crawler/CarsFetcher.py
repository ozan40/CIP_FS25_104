import time
import re
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from .CrawledCar import CrawledCar

# Quelle:
# https://medium.com/@asheeshmisra29/web-automation-selenium-webdriver-and-python-getting-started-part-3-a9c07143d36d
class CarsFetcher():
    def __init__(self):
        # Selenium WebDriver Setup
        options = Options()
        options.add_argument("--headless")  # Läuft ohne sichtbares Fenster
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def extract_price_details(self, text):
        price_keywords = ["Sehr guter Preis", "Guter Preis", "Fairer Preis", "Erhöhter Preis", "Hoher Preis"]
        for keyword in price_keywords:
            if keyword in text:
                return keyword
        return np.nan

    def extract_car_details(self, text):
        kilometer, gear, date, fuel, power, consumption, co2 = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

        km_match = re.search(r"(\d{1,3}(?:\.\d{3})?)\s*km", text)
        if km_match:
            kilometer = km_match.group(1) + " km"
            text = text.replace(km_match.group(0), "").strip()

        gear_keywords = ["Schaltgetriebe", "Automatik", "Halbautomatik"]
        for keyword in gear_keywords:
            if keyword in text:
                gear = keyword
                text = text.replace(keyword, "").strip()
                break

        date_match = re.search(r"(\d{2}/\d{4})", text)
        if date_match:
            date = date_match.group(1)
            text = text.replace(date_match.group(0), "").strip()

        fuel_keywords = ["Benzin", "Diesel", "Elektro", "Autogas (LPG)", "Elektro/Benzin", "Elektro/Diesel", "Sonstige",
                         "Erdgas (CNG)", "Ethanol", "Wasserstoff"]
        for keyword in fuel_keywords:
            if keyword in text:
                fuel = keyword
                text = text.replace(keyword, "").strip()
                break

        power_match = re.search(r"(\d{1,3})\s*kW\s*\((\d{1,3})\s*PS\)", text)
        if power_match:
            power = f"{power_match.group(1)} kW ({power_match.group(2)} PS)"
            text = text.replace(power_match.group(0), "").strip()

        consumption_match = re.search(r"(\d{1,2},\d)\s*l/100\s*km", text)
        if consumption_match:
            consumption = consumption_match.group(1) + " l/100 km"
            text = text.replace(consumption_match.group(0), "").strip()

        co2_match = re.search(r"(\d{1,3})\s*g/km", text)
        if co2_match:
            co2 = co2_match.group(1) + " g/km"
            text = text.replace(co2_match.group(0), "").strip()

        return kilometer, gear, date, fuel, power, consumption, co2

    def fetch(self):
        cars_element = []
<<<<<<< HEAD
        first_registration = np.arange(2010, 2023, 1)
=======
        first_registration = np.arange(2010, 2018, 1)
>>>>>>> origin/main
        pages = np.arange(1, 20, 1)

        for registration in first_registration:
            for page in pages:
                url = f"https://www.autoscout24.de/lst?atype=C&cy=D&damaged_listing=exclude&desc=0&fregfrom={registration}&ocs_listing=include&page={page}&powertype=kw&search_id=1dz1isvldxn&sort=standard&source=listpage_pagination&ustate=N%2CU"

                # Selenium öffnet die Seite
                self.driver.get(url)
                time.sleep(3)  # Warten, bis die Seite geladen ist

                # BeautifulSoup verarbeitet den HTML-Quellcode von Selenium
                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                for car in soup.select("article",
                                       class_="cldt-summary-full-item listing-impressions-tracking list-page-item ListItem_article__qyYw7"):
                    try:
                        brand_scrap = car.select_one("h2", class_="ListItem_title__ndA4s").contents[0].text
                        model_scrap = car.select_one("h2", class_="ListItem_title__ndA4s").contents[1].text
                        car_info_scrap = car.select_one("h2", class_="ListItem_title__ndA4s").contents[2].text
                        user_text_scrap = car.select_one("a", class_="ListItem_subtitle__VEw08").contents[1].text
                        price_scrap = car.select_one("p", class_="Price_price__APlgs PriceAndSeals_current_price__ykUpx").contents[0].text

                        price_evaluation_input = car.select_one("div", class_="scr-price-label PriceAndSeals_price_info__hXkBr p").contents[2].text
                        price_evaluation_scrap = self.extract_price_details(price_evaluation_input)

                        car_details_input = car.select_one("div",class_="VehicleDetailTable_container__XhfV1").contents[2].text
                        km_scrap, gear_scrap, date_scrap, fuel_scrap, power_scrap, consumption_scrap, co2_scrap = self.extract_car_details(car_details_input)

                        crawled = CrawledCar(
                            brand_scrap, model_scrap, car_info_scrap, user_text_scrap, price_scrap,
                            price_evaluation_scrap, km_scrap, gear_scrap, date_scrap, fuel_scrap, power_scrap,
                            consumption_scrap, co2_scrap
                        )
                        cars_element.append(crawled)

                    except AttributeError:
                        print("Attribute Error - Element is missing.")
                    except IndexError:
                        print("Index Error - List Problem.")

        return cars_element

    def close(self):
        self.driver.quit()  # Selenium schließen