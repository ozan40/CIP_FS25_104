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
from requests import get
from bs4 import BeautifulSoup
import re
from time import sleep
import random

brand_l = []
explanation_l = []
model_l = []
years_l = []
km_l = []
prices_l = []
hp_l = []
gear_l = []
fuel_l = []

def extract_car_details(text):
    details = {}

    # extract km
    km_keyword = "km"
    if km_keyword in text:
        km_index = text.index(km_keyword) + len(km_keyword)
        details['kilometer'] = text[:km_index].strip()
        text = text[km_index:].strip()

    # Extract gear
    gear_type = ["Manual", "Automatic", "Semi-automatic", "- Gear"]
    for keyword in gear_type:
        if keyword in text:
            # Wenn es nur "- Gear" ist, soll es ignoriert werden
            trans_index = text.index(keyword) + len(keyword)
            details['gear'] = text[:trans_index].strip()
            text = text[trans_index:].strip()
        else:
            details['gear'] = np.nan
            break

    # Extract date
    date_format = "MM/YYYY"
    date_parts = text.split("/", 1)
    if len(date_parts) == 2 and date_parts[0].isdigit() and date_parts[1][:4].isdigit():
        details['date'] = date_parts[0] + "/" + date_parts[1][:4]
        text = date_parts[1][4:].strip()
    else:
        details['date'] = np.nan

    # extract fuel
    fuel_keywords = ["Gasoline", "Diesel", "Electric", "LPG", "Electric/Gasoline", "Electric"]
    for keyword in fuel_keywords:
        if keyword in text:
            fuel_index = text.index(keyword) + len(keyword)
            details['fuel'] = text[:fuel_index].strip()
            text = text[fuel_index:].strip()
        else:
            details['fuel'] = np.nan
            break

    # extract ps
    power_parts = text.split(" ", 1)
    if len(power_parts) == 2:
        details['ps'] = power_parts[0] + " " + power_parts[1]
    else:
        details['ps'] = np.nan

    return details

# Scraping part
pages = np.arange(1, 21, 1)  # (1,2,3,…,20)
for page in pages:
    url = 'https://www.autoscout24.com/lst?atype=C&custtype=P&desc=0&page=' + str(page)
    soup = BeautifulSoup(requests.get(url).text, parser="html.parser", features="lxml")

    for car in soup.select("article",class_="cldt-summary-full-item listing-impressions-tracking list-page-item ListItem_article__qyYw7"):
        # scraping brand and saving in list
        brand = car.select_one("h2",class_="ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I").contents[0].get_text(strip=True)
        brand_l.append(brand)
        # scraping ,pdeö and saving in list
        model = car.select_one("h2", class_="ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I").contents[1].get_text(strip=True)
        model_l.append(model)
        # scraping description and saving in list
        description = car.select_one("h2", class_="ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I").contents[2].get_text(strip=True)
        explanation_l.append(description)
        # scraping price and saving in list
        price = car.select_one("p", class_="Price_price__APlgs PriceAndSeals_current_price__ykUpx").contents[0].get_text(strip=True)
        prices_l.append(price)

        # Here, due to span elements, every element was formed to one element in output
        # the whole construct is given to variable kilometer and then extract_car_details() is called to extract the information
        try:
            kilometer = car.div.find("div", class_="ListItem_listing__g3sc6").contents[2].text.strip("")
            car_details = extract_car_details(kilometer)

            for ind, val in car_details.items():
                if ind == "kilometer":
                    km_l.append(val)
                elif ind == "gear":
                    gear_l.append(val)
                elif ind == "date":
                    years_l.append(val)
                elif ind == "fuel":
                    fuel_l.append(val)
                elif ind == "ps":
                    hp_l.append(val)

        except AttributeError:
            km_l.append(np.nan)
            gear_l.append(np.nan)
            years_l.append(np.nan)
            fuel_l.append(np.nan)
            hp_l.append(np.nan)



