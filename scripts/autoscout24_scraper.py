from bs4 import BeautifulSoup
import re
import time
import numpy as np
import pandas as pd
import requests

class CrawledCar():
    # Konstruktur initialisieren und brand, model, description, price, kilometer, gear, year, fuel, hp übergeben
    def __init__(self,brand, model, car_info,user_text, price,price_evaluation, km, gear, date, fuel, power, consumption, co2):
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

class CarsFetcher():
    def extract_price_details(self, text):

        # Preisbewertungs-Schlüsselwörter
        price_keywords = ["Sehr guter Preis", "Guter Preis", "Fairer Preis", "Erhöhter Preis", "Hoher Preis"]

        # Preisbewertung extrahieren
        for keyword in price_keywords:
            if keyword in text:
                return keyword
        # Falls keine Bewertung gefunden wird
        return np.nan

    def extract_car_details(self, text):
        kilometer, gear, date, fuel, power, consumption, co2 = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

        # 🔹 **Kilometer extrahieren (Format: "92.500 km")**
        km_match = re.search(r"(\d{1,3}(?:\.\d{3})?)\s*km", text)
        if km_match:
            kilometer = km_match.group(1) + " km"
            text = text.replace(km_match.group(0), "").strip()

        # 🔹 **Getriebe extrahieren (Schaltgetriebe, Automatik, etc.)**
        gear_keywords = ["Schaltgetriebe", "Automatik", "Halbautomatik"]
        for keyword in gear_keywords:
            if keyword in text:
                gear = keyword
                text = text.replace(keyword, "").strip()
                break

        # 🔹 **Publikationsdatum extrahieren (Format: MM/YYYY)**
        date_match = re.search(r"(\d{2}/\d{4})", text)
        if date_match:
            date = date_match.group(1)
            text = text.replace(date_match.group(0), "").strip()

        # 🔹 **Kraftstoffart extrahieren**
        fuel_keywords = ["Gasoline", "Diesel", "Electric", "LPG", "Electric/Gasoline", "Others", "CNG", "Ethanol"]
        for keyword in fuel_keywords:
            if keyword in text:
                fuel = keyword
                text = text.replace(keyword, "").strip()
                break

        # 🔹 **Leistung extrahieren (Format: "128 kW (174 PS)")**
        power_match = re.search(r"(\d{1,3})\s*kW\s*\((\d{1,3})\s*PS\)", text)
        if power_match:
            power = f"{power_match.group(1)} kW ({power_match.group(2)} PS)"
            text = text.replace(power_match.group(0), "").strip()

        # 🔹 **Verbrauch extrahieren (Format: "5,3 l/100 km")**
        consumption_match = re.search(r"(\d{1,2},\d)\s*l/100\s*km", text)
        if consumption_match:
            consumption = consumption_match.group(1) + " l/100 km"
            text = text.replace(consumption_match.group(0), "").strip()

        # 🔹 **CO₂-Emissionen extrahieren (Format: "138 g/km")**
        co2_match = re.search(r"(\d{1,3})\s*g/km", text)
        if co2_match:
            co2 = co2_match.group(1) + " g/km"
            text = text.replace(co2_match.group(0), "").strip()

        # 🔥 **Entpacke die Werte als einzelne Rückgabewerte**
        return kilometer, gear, date, fuel, power, consumption, co2

    def fetch(self):
        cars_element = []
        first_registration = np.arange(2010, 2018, 1)
        pages = np.arange(1, 21, 1)
        for registration in first_registration:
            for page in pages:
                url = "https://www.autoscout24.de/lst?atype=C&cy=D&damaged_listing=exclude&desc=0&fregfrom=" + str(
                    registration) + "&ocs_listing=include&page=" + str(
                    page) + "&powertype=kw&search_id=1dz1isvldxn&sort=standard&source=listpage_pagination&ustate=N%2CU"
                soup = BeautifulSoup(requests.get(url).text, parser="html.parser", features="lxml")
                time.sleep(1)

                for car in soup.select("article",
                                       class_="cldt-summary-full-item listing-impressions-tracking list-page-item ListItem_article__qyYw7"):
                    try:
                        brand_scrap = car.select_one("h2",
                                               class_="ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I").contents[
                            0].text
                        model_scrap = car.select_one("h2",
                                               class_="ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I").contents[
                            1].text
                        car_info_scrap = car.select_one("h2",
                                                  class_="ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I").contents[
                            2].text
                        user_text_scrap = car.select_one("a", class_="ListItem_subtitle__VEw08").contents[1].text

                        price_scrap = \
                        car.select_one("p", class_="Price_price__APlgs PriceAndSeals_current_price__ykUpx").contents[0].text
                        price_evaluation_input = \
                        car.select_one("div", class_="scr-price-label PriceAndSeals_price_info__hXkBr p").contents[2].text
                        price_evaluation_scrap = CarsFetcher.extract_price_details(self, price_evaluation_input)

                        car_details_input = car.select_one("div", class_="VehicleDetailTable_container__XhfV1").contents[
                            2].text
                        km_scrap, gear_scrap, date_scrap, fuel_scrap, power_scrap, consumption_scrap, co2_scrap = CarsFetcher.extract_car_details(self, car_details_input)

                    # except AttributeError:
                    #     print("Attribute Error")
                    #
                    #
                    except IndexError:
                        user_text = np.nan

                    crawled = CrawledCar(brand_scrap, model_scrap, car_info_scrap, user_text_scrap,
                                         price_scrap,price_evaluation_scrap,km_scrap, gear_scrap,
                                         date_scrap, fuel_scrap, power_scrap, consumption_scrap, co2_scrap  )
                    cars_element.append(crawled)
        return cars_element

fetcher = CarsFetcher()
cars = fetcher.fetch()

brand_list = []
model_list = []
car_info_list = []
user_text_list = []
price_list = []
price_evaluation_list = []
gear_list = []
date_list = []
fuel_list = []
power_list = []
consumption_list = []
co2_list = []
km_list = []

for car in cars:
    brand_list.append(car.brand)
    model_list.append(car.model)
    car_info_list.append(car.car_info)
    user_text_list.append(car.user_text)
    price_list.append(car.price)
    price_evaluation_list.append(car.price_evaluation)
    km_list.append(car.kilometer)
    gear_list.append(car.gear)
    date_list.append(car.date)
    fuel_list.append(car.fuel)
    power_list.append(car.power)
    consumption_list.append(car.consumption)
    co2_list.append(car.co2)

df_cars = pd.DataFrame({
    'Brand':brand_list,
    'Model':model_list,
    'Car_info': car_info_list,
    'User_Desc': user_text_list,
    'Price':price_list,
    'Price_Eval': price_evaluation_list,
    'Kilometer':km_list,
    'Gear_Type':gear_list,
    'YearMonth':date_list,
    'Fuel_Type':fuel_list,
    'Horsepower':power_list,
    'Consumption': consumption_list,
    'CO2_Emission': co2_list
})
print(df_cars.head())
df_cars.to_csv("crawler_output.csv",sep = ";")

# Code von https://docs.python.org/3/library/csv.html#csv.writer
# with open('crawler_output.csv', 'w', newline='') as csvfile:
#     carswriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#     for car in fetcher.fetch():
#         carswriter.writerow([car.brand, car.model, car.price, car.description, car.kilometer,car.gear, car.year, car.fuel, car.hp] )