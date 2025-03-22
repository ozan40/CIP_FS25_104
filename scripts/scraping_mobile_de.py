# -----------------------------
# -----Create virtual environment
# -----------------------------

# python -m venv venv
# source venv/bin/activate

# Install packages into virtual environment

# pip3 install beautifulsoup4 (HTML parser)

# Create requirement.txt
# pip3 freeze > requirements.txt

# Install from requirements.txt
# pip3 install -r requirements.txt

# -----------------------------
# -----Check installed packages
# -----------------------------

# pip3 list

# -----------------------------
# ----- Import modules
# -----------------------------

import re
import time

#import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
#from crawler.CrawledCar import CrawledCar

url = "https://suchen.mobile.de/fahrzeuge/search.html?dam=false&isSearchRequest=true&ref=quickSearch&s=Car&sb=rel&vc=Car"

print(url)

class CrawledCar():
    # Konstruktur initialisieren und brand, model, description, price, kilometer, gear, year, fuel, hp, etc. übergeben
    def __init__(self, brand = None, model= None, car_info= None, user_text= None, price= None, price_evaluation= None,
                 km= None, gear= None, date= None, fuel= None, power= None,
                 consumption= None, co2= None):
        self.brand = brand
        self.model = model
        self.car_info = car_info
        self.user_text = user_text
        self.price = price
        self.price_evaluation = price_evaluation
        self.kilometer = km
        self.gear = gear
        self.date = date
        self.fuel = fuel
        self.power = power
        self.consumption = consumption
        self.co2 = co2

class carFetcher():

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.all_cars = []

    @staticmethod
    def extract_info(car_html, tag: str = None, class_input: str = None, attrs: dict = None) -> str | None:
        try:
            return car_html.find(tag, class_=class_input).text
        except AttributeError:
            return None

    def fetch_page(self):
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        all_cars_html = soup.find_all('article', class_="A3G6X vTKPY")
        #fuel_keywords = ["Benzin", "Diesel", "Elektro", "Autogas (LPG)", "Elektro/Benzin", "Elektro/Diesel", "Sonstige",
        #                "Erdgas (CNG)", "Ethanol", "Wasserstoff"]

        cars = []

        url = 'https://suchen.mobile.de/'
        all_links = soup.find_all('a', class_='FWtU1 YIC4W rqEvz', href = True)
        
        for link in all_links: 
            full_url = urljoin(url, link['href'])
            print(full_url)

        for car in all_cars_html[2]:  # change this not hard coded

            list_info = carFetcher.extract_info(car, 'div', 'HaBLt')
            price = carFetcher.extract_info(car, 'span', 't5RmH')
            brand = carFetcher.extract_info(car, 'span', 'LBG5d')
           
            if list_info:
                list_info = list_info.split("•")
                list_info = [element.replace("\xa0", " ").strip() for element in list_info]
                hp = next((element for element in list_info if " kW " in element), None)
                km = next((element for element in list_info if " km" in element), None)
                year = next((element for element in list_info if "EZ " in element), None)
           
            else:
                hp = None
                km = None
                year = None

                # print(f"Extracted Info: {hp}, {km}, {year}, {price}, {brand}")  # Debugging

            crawled_object = CrawledCar(power = hp, km = km, date = year, price = price, brand = brand)
            cars.append(crawled_object)
            #idx += 1

        #print(f'Returning {len(cars)} cars from this page")
        return cars
    

        

    def fetch_multiple_pages(self, url, max_pages=1):
        self.driver.get(url)
        #print(f"Fetching from: {url}")
        for i in range(max_pages):
            time.sleep(5)  # Allow time for the page to load
            cars_on_page = self.fetch_page()  # Fetch a single page

            if cars_on_page:
                self.all_cars.extend(cars_on_page)
            else:
                break

            time.sleep(10)  # Allow time for the button to become clickable

            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='pagination:next']")))
            except:
                print("No 'Next' button found, stopping.")
                break

        self.driver.quit()
        # print(f"Total cars collected: {len(self.all_cars)}")
        return self.all_cars


def main():
    test = carFetcher()
    car_list = test.fetch_multiple_pages(url)

    print(car_list)
    for car in car_list:
        print(vars(car))
    return car_list

if __name__ == '__main__':
    dataset = main()

