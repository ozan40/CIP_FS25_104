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
import os
import sys
import time
import json
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
from fake_useragent import UserAgent
import random
from urllib.parse import urljoin
from CrawledCar import CrawledCar


class CrawledCarWithNone(CrawledCar):
    '''
    Inherite same structure as in CrawledCar but change default value to None
    '''
    def __init__(self, brand = None, model= None, car_info= None, user_text= None, price= None, price_evaluation= None,
                 km= None, gear= None, date= None, fuel= None, power= None,
                 consumption= None, co2= None):
        super().__init__(brand, model, car_info, user_text, price, price_evaluation,
                         km, gear, date, fuel, power, consumption, co2)



class carFetcher():

    def __init__(self):
        # Set up Firefox options
        options = Options()
        
        options.set_preference("permissions.default.image", 2)  # Disable images
        options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")  # Disable Flash
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        options.set_preference("dom.webdriver.enabled", False)  # Disable automation flag
        options.set_preference("useAutomationExtension", False)
        options.headless = True  # Enable headless mode for faster execution
        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f'user-agent={user_agent}')

        service = Service('/usr/local/bin/geckodriver')
        self.driver = webdriver.Firefox(service=service, options=options)

        #self.driver = webdriver.Firefox()
        self.all_cars = []

    @staticmethod
    def extract_info(car_html, tag: str = None, class_input: str = None, attrs: dict = None) -> str | None:
        try:
            return car_html.find(tag, class_=class_input).text
        except AttributeError:
            return None
    
    def extract_brand_names(self):
        # Load the JSON file retrieved from mobile de
        with open("../miscellaneous/car_brand.json", "r") as file:
            data = json.load(file)

        # Extract the "ms" list from the nested "data" key
        ms_list = data.get("data", {}).get("ms", [])
        # Extract only the 'n' (name) values
        brand_names = [item.get("n") for item in ms_list]
        return brand_names
    
    def extract_names(self, brand_list, brand):
        
        if brand:
            brand_name = []
            type_name = []

            for element in brand.split(" "):
                if element in brand_list:
                    brand_name.append(element)
                else:
                    type_name.append(element)
            return brand_name, type_name
        else:
            return None, None
        
    def following_link(self, car_html):
        """
        Follows individual links of each car listing to detailed site. This access is blocked possibily due to bot detection. 
        No hidden api can be found to sidestep this approach :(
        This function is not further used.
        """
 

        url = 'https://suchen.mobile.de/'
        link = car_html.find('a', class_='FWtU1 YIC4W rqEvz', href = True)
        
        try: 
            full_url = urljoin(url, link['href'])
            print("fetiching:" , {full_url} )

        except: 
            return None
            
        try:
               # Wait for the page to load and fetch cars
            response = requests.get(full_url)
            print(response.status_code)

            self.driver.get(full_url)
            time.sleep(random.uniform(8, 15))

            
            try:
                # Wait for the "Mehr Anzeigen" button to be present

                mehr_anzeigen_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@type='button' and contains(@class, 'FWtU1') and contains(@class, 'drxl5') and contains(@class, 'XY6XP') and @role='link']"))
                )
                # Get the new URL
                new_url = self.driver.current_url
                print("New URL:", new_url)
                # Click the button using JavaScript
                self.driver.execute_script("arguments[0].click();", mehr_anzeigen_button)
                new_url_afer_click = self.driver.current_url
                print("New URL:", new_url_afer_click)
                # Wait for the page to load after clicking
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@type='button' and contains(@class, 'FWtU1') and contains(@class, 'drxl5') and contains(@class, 'XY6XP') and @role='link']"))
                )
                print(f"inspect button {self.driver.current_url}")
                
            except Exception as e:
                print(f"Error interacting with 'Mehr Anzeigen' button: {e}")
                #with open("page_source.html", "w", encoding="utf-8") as file:
                #     file.write(self.driver.page_source)
                #print("HTML saved to page_source.html")
                
                
        except:
            print("ups didn't work")   
        fuel_type = carFetcher.extract_info(self.driver, 'dd', 'nuAmT')
        print(f"Fuel type: {fuel_type}")

        return fuel_type

    def fetch_page(self):
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        all_cars_html = soup.find_all('article', class_="A3G6X vTKPY")

        cars = []
        
        fuel_keywords = ["Benzin", "Diesel", "Elektro", "Autogas (LPG)", "Hybrid (Diesel/Elektro)","Hybrid (Benzin/Elektro)", "Elektro/Diesel", "Andere",
                         "Erdgas (CNG)", "Ethanol (FFV, E85 etc.)", "Wasserstoff", "Plug-in-Hybrid"]

        for car in all_cars_html: 

            list_info = carFetcher.extract_info(car, 'div', 'HaBLt')
            price_info = carFetcher.extract_info(car, 'span', 't5RmH')
            price = re.sub(r'\D', '', price_info) if price_info else None
            print(f"{price=}")
            brand = carFetcher.extract_info(car, 'span', 'LBG5d')
            
            if brand:
                brand_name = brand.split(" ")[0]

                type_name  = " ".join(brand.split(" ")[1:])

            else:
                brand_name = None
                type_name = None
            #split brand and type 
            #brand_list = self.extract_brand_names()
            #brand_name, type_name=  self.extract_names(self, brand_list, brand)
            car_info = carFetcher.extract_info(car, 'span', 'Z_aNr')
            price_evaluation = carFetcher.extract_info(car, 'div', '_u77E XtrJR')
            #fuel = self.following_link(car)

            if list_info:
                list_info = list_info.split("•")
                list_info = [element.replace("\xa0", " ").strip() for element in list_info]
                hp = next((element for element in list_info if " PS" in element), None)
                if hp:
                    hp = re.search(r'\((\d+)\sPS\)', hp).group(1)
                    print(f"{hp=}")
                km = next((element for element in list_info if " km" in element), None)
                if km:
                    km = re.sub(r'\D', '', km)
                    print(f"{km=}")
                year = next((element for element in list_info if "EZ " in element), None)
                if year: 
                    year = re.sub(r'[a-zA-Z]', '', year).strip()
                    print(f"{year=}")
                fuel = next((element for element in list_info if element in fuel_keywords), None)

           
            else:
                hp = None
                km = None
                year = None
                fuel = None
                

                # print(f"Extracted Info: {hp}, {km}, {year}, {price}, {brand}")  # Debugging
            crawled_object = CrawledCarWithNone(power = hp, km = km, date = year, price = price, brand = brand_name, model = type_name, fuel = fuel, car_info= car_info,
                                        price_evaluation=price_evaluation)
            cars.append(crawled_object)
            #idx += 1

        #print(f'Returning {len(cars)} cars from this page")
        return cars

    def interact_next_button(self):
        """Interacts with the 'Next' button up to max_interactions times."""

        try:
                # Wait for the "Next" button to be present
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@data-testid='pagination:next']"))
                )

                # Click the button using JavaScript
                self.driver.execute_script("arguments[0].click();", next_button)

                # Wait for the page to load
                time.sleep(5)
        except Exception as e:
                print(f"No 'Next' button found or error occurred: {e}")
                      
        
    def change_category_url(self, url, idx):
        """Starting URL should by one category to ensure corerect link.
        Adjusts the URL to increment the page number by 1.
        """

        categories = ["OffRoad", "EstateCar", "Van", "SportsCar", "SmallCar",
                  "Limousine", "OtherCar"]
        # Replace the old page number with the new one
        changed_url =re.sub(r'c=[^&]+', f'c={categories[idx]}', url)
    
        return changed_url
   
    
    def fetch_multiple_pages(self, url, max_pages=50):
        for cat in range(7):
            changed_url = self.change_category_url(url, cat)
            self.driver.get(changed_url)
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
                    # Use the 'Next' button to navigate
                    self.interact_next_button()
                except:
                    print("Couldn't interact with next button")
             

            

        self.driver.quit()
        # print(f"Total cars collected: {len(self.all_cars)}")
        return self.all_cars


def main():
    # Set the working directory to the directory of the current file
    #script_dir = os.path.dirname(os.path.abspath(__file__))
    #os.chdir(script_dir)
    print(f"Working directory set to: {os.getcwd()}")
#    Print the sys.path to see what paths are appended
    print("Python sys.path:")
    for path in sys.path:
        print(f"  {path}")
    print("-"*20)   
    url = "https://suchen.mobile.de/fahrzeuge/search.html?c=Cabrio&dam=false&isSearchRequest=true&ref=dsp&s=Car&sb=rel&vc=Car"
    mobile_de = carFetcher()
    car_list = mobile_de.fetch_multiple_pages(url)

    # saves it to root becaus i added sys.path.append("path to root") to this script trying to import crawler
    # Export car_list to a CSV file
    with open('car_mobile.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header row (attribute names)
        if car_list:
            writer.writerow(vars(car_list[0]).keys())

        for car in car_list:
             # Check if the row is not empty (i.e., at least one value is not None or empty)
            row = list(vars(car).values())
            if any(row):  # If any value in the row is non-empty
                writer.writerow(row)

if __name__ == '__main__':
    dataset = main()