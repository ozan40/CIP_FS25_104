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
import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import random
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
        # Set up Firefox options
        firefox_options = Options()
        firefox_options.set_preference("permissions.default.image", 2)  # Disable images
        firefox_options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")  # Disable Flash
        firefox_options.headless = True  # Enable headless mode for faster execution

        service = Service('/usr/local/bin/geckodriver')
        self.driver = webdriver.Firefox(service=service, options=firefox_options)

        #self.driver = webdriver.Firefox()
        self.all_cars = []

    @staticmethod
    def extract_info(car_html, tag: str = None, class_input: str = None, attrs: dict = None) -> str | None:
        try:
            return car_html.find(tag, class_=class_input).text
        except AttributeError:
            return None

    def following_link(self, soup):

 

        url = 'https://suchen.mobile.de/'
        link = soup.find('a', class_='FWtU1 YIC4W rqEvz', href = True)
        
        try: 
            full_url = urljoin(url, link['href'])
            print("fetiching:" , {full_url} )
            try: 
                req = requests.get(full_url, timeout=10)  # Add a timeout to prevent hanging
                req.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
                print(req[1])
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch {full_url}: {e}")
        except: 
            return None
            
        try:
                # Navigate to link 
                self.driver.get(full_url)
                soup_sublink = BeautifulSoup(self.driver.page_source, 'html.parser')
            
                try:

                    next_button = WebDriverWait(self.driver, 10).until(
                     EC.visibility_of_element_located((By.CSS_SELECTOR, "div.VXw4m button.FWtU1"))
)
                    #next_button = WebDriverWait(self.driver, 10).until(
                    #EC.element_to_be_clickable((By.CSS_SELECTOR, "div.VXw4m button.FWtU1"))
                    #)
                    next_button.click()
                    print("found button")
                except:
                    print("No 'Mehr Anzeigen' button found, stopping.")
                
                fuel_type = carFetcher.extract_info(soup_sublink, 'dd', 'nuAmT')
                print(fuel_type)
        except:
            print("ups didn't work")   
        return fuel_type

    def fetch_page(self):
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        all_cars_html = soup.find_all('article', class_="A3G6X vTKPY")

        cars = []
        
        fuel_keywords = ["Benzin", "Diesel", "Elektro", "Autogas (LPG)", "Elektro/Benzin", "Elektro/Diesel", "Sonstige",
                         "Erdgas (CNG)", "Ethanol", "Wasserstoff"]

        for car in all_cars_html: 

            list_info = carFetcher.extract_info(car, 'div', 'HaBLt')
            price_info = carFetcher.extract_info(car, 'span', 't5RmH')
            price = price_info.replace("\xa0", " ").strip() if price_info else None
            brand = carFetcher.extract_info(car, 'span', 'LBG5d')
            car_info = carFetcher.extract_info(car, 'span', 'Z_aNr')
            price_evaluation = carFetcher.extract_info(car, 'div', '_u77E XtrJR')
            #fuel = self.following_link(car)

            if list_info:
                list_info = list_info.split("•")
                list_info = [element.replace("\xa0", " ").strip() for element in list_info]
                hp = next((element for element in list_info if " kW " in element), None)
                km = next((element for element in list_info if " km" in element), None)
                year = next((element for element in list_info if "EZ " in element), None)
                fuel = next((element for element in list_info if element in fuel_keywords), None)

           
            else:
                hp = None
                km = None
                year = None
                fuel = None

                # print(f"Extracted Info: {hp}, {km}, {year}, {price}, {brand}")  # Debugging
            crawled_object = CrawledCar(power = hp, km = km, date = year, price = price, brand = brand, fuel = fuel, car_info= car_info,
                                        price_evaluation=price_evaluation)
            cars.append(crawled_object)
            #idx += 1

        #print(f'Returning {len(cars)} cars from this page")
        return cars

        
        
    
    
    def fetch_multiple_pages(self, url, max_pages=50):
        self.driver.get(url)
        #print(f"Fetching from: {url}")
        for i in range(max_pages):
            # Wait for the page to load and fetch cars
            time.sleep(5)
            cars_on_page = WebDriverWait(self.driver, 10).until(
                lambda driver: self.fetch_page()  # Fetch cars when the page is ready: explain this code later
        )
            if cars_on_page:
                self.all_cars.extend(cars_on_page)
            else:
                break

            
            try:
                # Wait for the "Next" button to be present

                next_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@data-testid='pagination:next']"))
                )

                # Click the button using JavaScript
                self.driver.execute_script("arguments[0].click();", next_button)

                # Wait for the page to load after clicking
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@data-testid='pagination:next']"))
                )
                print(f"inspect button {self.driver.current_url}")
            except Exception as e:
                print(f"Error interacting with 'Next' button: {e}")
                #with open("page_source.html", "w", encoding="utf-8") as file:
                #     file.write(self.driver.page_source)
                #print("HTML saved to page_source.html")
                break
            

        self.driver.quit()
        # print(f"Total cars collected: {len(self.all_cars)}")
        return self.all_cars


def main():
    test = carFetcher()
    car_list = test.fetch_multiple_pages(url)

    # Export car_list to a CSV file
    with open('car_list.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header row (attribute names)
        if car_list:
            writer.writerow(vars(car_list[0]).keys())

        # Write the data rows (attribute values)
        for car in car_list:
            writer.writerow(vars(car).values())

if __name__ == '__main__':
    dataset = main()

