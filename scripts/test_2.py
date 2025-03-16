# Crawler extracts data from a website
# 1. call the website with html-code
# 2. extract from this html-code the data
# Python sends a request to the server of the website and then server sends a response
# This response is a HTML-code, then the code is read and we extract the relevant data from this.

# Beispiel um Crawler zu verwenden:
# 1. Python Program which extracs from internet site the actual stock prices which calculates my actual depot value
# 2. Or to read a news site and write all headings into a csv file to get an overview which news are published on which days
# 3. extract products in a huge excel file which contains all products which are relevant for me.

# Holl mir Website und zeig mir den HTML Code ein, dazu verwenden wir request library
# Request modul kümmert sich drum, dass wir die Website zu holen.

# Jetzt crawlen wir daten aus autoscout Titel, Kommentar, Preis, Veröffentlichungsdatum, Kilometerstand, Getriebe, BenzinDiesel, PS, Verbrauch, Anbieter, Gemeinde, PLZ, MFK, Garantie
# zuerst laden wir nun den HTML code herunter mithilfe von package requests, damit wir im zweiten Schritt den HTML zerlegen können.

# load libraries
import pandas as pd
import numpy as np
import requests
from dateutil.parser import parser
from requests import get
from bs4 import BeautifulSoup
import re
import time

def extract_price_details(text):

    # Preisbewertungs-Schlüsselwörter
    price_keywords = ["Sehr guter Preis", "Guter Preis", "Fairer Preis", "Erhöhter Preis", "Hoher Preis"]

    # Preisbewertung extrahieren
    for keyword in price_keywords:
        if keyword in text:
            return keyword
    # Falls keine Bewertung gefunden wird
    return np.nan

def extract_car_details(text):
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

price_eval = []
first_registration = np.arange(2010, 2011, 1)
pages = np.arange(1, 10, 1)
for registration in first_registration:
    for page in pages:
        url = "https://www.autoscout24.de/lst?atype=C&cy=D&damaged_listing=exclude&desc=0&fregfrom=" +str(registration) + "&ocs_listing=include&page="+ str(page)+"&powertype=kw&search_id=1dz1isvldxn&sort=standard&source=listpage_pagination&ustate=N%2CU"
        soup = BeautifulSoup(requests.get(url).text, parser="html.parser", features="lxml")
        time.sleep(1)

        for car in soup.select("article", class_ = "cldt-summary-full-item listing-impressions-tracking list-page-item ListItem_article__qyYw7"):
            try:
                brand = car.select_one("h2", class_ = "ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I").contents[0].text
                model = car.select_one("h2", class_ = "ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I").contents[1].text
                car_info = car.select_one("h2", class_ = "ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I").contents[2].text
                user_text = car.select_one("a", class_="ListItem_subtitle__VEw08").contents[1].text

                price = car.select_one("p", class_ = "Price_price__APlgs PriceAndSeals_current_price__ykUpx").contents[0].text
                price_evaluation_input = car.select_one("div", class_ = "scr-price-label PriceAndSeals_price_info__hXkBr p").contents[2].text
                price_evaluation = extract_price_details(price_evaluation_input)

                car_details_input = car.select_one("div", class_ = "VehicleDetailTable_container__XhfV1").contents[2].text
                km, gear, date, fuel, power, consumption, co2 = extract_car_details(car_details_input)
                print(date)
            # except AttributeError:
            #     print("Attribute Error")
            #
            #
            except IndexError:
                user_text = np.nan


