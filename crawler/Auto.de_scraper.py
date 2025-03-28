import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed

class WebAutomation:
    def __init__(self, headless=False):
        options = Options()
        if headless:
            options.add_argument('--start-maximized')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def accept_cookies(self):
        time.sleep(1)
        cookie_buttons = self.driver.find_elements(By.XPATH, "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'zustimmen')]")
        if cookie_buttons:
            cookie_buttons[0].click()

    def zoom_out_css(self, scale=0.75):
        script = f"""
            document.body.style.transform = "scale({scale})";
            document.body.style.transformOrigin = "0 0";
            document.body.style.width = "{100/scale}%";
        """
        self.driver.execute_script(script)

    def slow_scroll(self, scroll_pause_time=0.2, scroll_increment=400):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        while current_position < last_height:
            self.driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(scroll_pause_time)
            current_position += scroll_increment
            last_height = self.driver.execute_script("return document.body.scrollHeight")

    def go_to_next_page(self):
        try:
            next_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.Pagination__goForward___V2fm8'))
            )
            next_button.click()
            time.sleep(random.uniform(1.5, 2.5))
            return True
        except:
            return False

    def quit(self):
        self.driver.quit()

class CarFetcher:
    def __init__(self, driver):
        self.driver = driver

    def get_text_or_none(self, element, selector):
        try:
            return element.find_element(By.CSS_SELECTOR, selector).text.strip()
        except:
            return None

    def extract_brand_model(self, brand_model_text):
        if not brand_model_text:
            return None, None
        words = brand_model_text.split(" ")
        if words[0] in ["Range", "Land"] and len(words) > 1:
            brand = " ".join(words[:2])
            model = " ".join(words[2:]) if len(words) > 2 else None
        else:
            brand = words[0]
            model = " ".join(words[1:]) if len(words) > 1 else None
        return brand, model

    def get_current_price(self, car):
        selector = 'div.VechiclePriceItem__priceItemBuy___EbiJT a.VechiclePriceItem__priceItemPrice___rbTmA span.VehicleFormattedPrice__container___NYXO4 span.FormattedNumber__formattedNumber___iNXv2 span'
        price_element = car.find_elements(By.CSS_SELECTOR, selector)
        return price_element[0].text.strip() if price_element else None

    def get_car_data(self, car):
        brand_model_text = self.get_text_or_none(car, 'h4[class*="VehicleTitle__manufacturerModel"]')
        brand, model = self.extract_brand_model(brand_model_text)

        properties = car.find_elements(By.CSS_SELECTOR, 'div.VehicleProperty__carProp___nBAOW span')
        km = properties[0].text.strip() if len(properties) > 0 else None
        build_year = properties[1].text.strip() if len(properties) > 1 else None
        transmission = properties[2].text.strip() if len(properties) > 2 else None
        fuel = properties[3].text.strip() if len(properties) > 3 else None
        power = properties[4].text.strip() if len(properties) > 4 else None
        raw_consumption_emission = properties[5].text.strip() if len(properties) > 5 else None

        consumption = emission = None
        if raw_consumption_emission:
            parts = raw_consumption_emission.replace("\n", ",").split(",")
            for part in parts:
                part = part.strip()
                if "l/100km" in part:
                    consumption = part
                elif "g CO2/km" in part:
                    emission = part

        current_price = self.get_current_price(car)

        return {
            'Brand': brand,
            'Model': model,
            'Kilometers': km,
            'BuildYear': build_year,
            'Transmission': transmission,
            'Fuel': fuel,
            'Power': power,
            'l/Km': consumption,
            'Emission': emission,
            'CurrentPrice': current_price
        }

def build_search_url(base_url, filter_dict):
    return f"{base_url}?{urlencode(filter_dict)}"

def scrape_with_filter(filter_set):
    search_url = build_search_url("https://www.auto.de/search", filter_set)
    print(f"[START] Scraping: {search_url}")

    browser = WebAutomation(headless=True)  # Of False als je wil zien wat er gebeurt
    fetcher = CarFetcher(browser.driver)

    try:
        browser.driver.get(search_url)
        browser.accept_cookies()
        browser.zoom_out_css(0.75)

        all_car_data = []
        for page_number in range(1, 21):  # max 10 pagina's per filter
            browser.slow_scroll()
            car_listings = browser.driver.find_elements(By.CSS_SELECTOR, 'section.VehicleSmallCard__vehicle____C5Tg')
            if not car_listings:
                break

            page_car_data = [fetcher.get_car_data(car) for car in car_listings[:15]]
            all_car_data.extend(page_car_data)

            if not browser.go_to_next_page():
                break

        print(f"[DONE] Filter: {filter_set} — {len(all_car_data)} cars scraped")
        return all_car_data

    finally:
        browser.quit()


def scrape_auto_de_parallel():
    filters = [
        {"firstRegistrationYearFrom": "2014"},
        {"firstRegistrationYearFrom": "2015"},
        {"firstRegistrationYearFrom": "2016"},
        {"firstRegistrationYearFrom": "2017"},
        {"firstRegistrationYearFrom": "2018"},
        {"firstRegistrationYearFrom": "2019"},
        {"firstRegistrationYearFrom": "2020"},
        {"firstRegistrationYearFrom": "2021"},
        {"firstRegistrationYearFrom": "2022"},
        {"firstRegistrationYearFrom": "2023"},
        {"firstRegistrationYearFrom": "2024"},
    ]

    all_data = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(scrape_with_filter, f) for f in filters]
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_data.extend(result)

    df = pd.DataFrame(all_data)
    df.to_csv('car_data_parallel.csv', index=False)
    print(f"\n[SAVED] Total cars scraped: {len(df)}")

if __name__ == "__main__":
    scrape_auto_de_parallel()
