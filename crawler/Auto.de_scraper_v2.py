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

# --- Helpers ---
def build_search_url(base_url, filter_dict):
    return f"{base_url}?{urlencode(filter_dict)}"

def normalize_identifier(data):
    def clean(x):
        return x.strip().lower() if isinstance(x, str) else x
    return tuple(clean(data[k]) for k in ['Brand', 'Model', 'Kilometers', 'CurrentPrice'])

# --- WebAutomation ---
class WebAutomation:
    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def accept_cookies(self):
        time.sleep(1)
        buttons = self.driver.find_elements(By.XPATH, "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'zustimmen')]")
        if buttons:
            buttons[0].click()

    def zoom_out_css(self, scale=0.75):
        script = f"""
            document.body.style.transform = "scale({scale})";
            document.body.style.transformOrigin = "0 0";
            document.body.style.width = "{100/scale}%";
        """
        self.driver.execute_script(script)

    def slow_scroll(self, pause=0.2, increment=400):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        current = 0
        while current < last_height:
            self.driver.execute_script(f"window.scrollTo(0, {current});")
            time.sleep(pause)
            current += increment
            last_height = self.driver.execute_script("return document.body.scrollHeight")

    def go_to_next_page(self):
        try:
            current_url = self.driver.current_url
            next_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.Pagination__goForward___V2fm8'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", next_btn)
            next_btn.click()
            WebDriverWait(self.driver, 10).until(EC.url_changes(current_url))
            time.sleep(random.uniform(1.5, 2.5))
            return True
        except Exception as e:
            print(f"[WARN] Cannot go to next page: {e}")
            return False

    def quit(self):
        self.driver.quit()

# --- CarFetcher ---
class CarFetcher:
    def __init__(self, driver):
        self.driver = driver

    def get_text_or_none(self, element, selector):
        try:
            return element.find_element(By.CSS_SELECTOR, selector).text.strip()
        except:
            return None

    def extract_brand_model(self, text):
        if not text:
            return None, None
        words = text.split(" ")
        if words[0] in ["Range", "Land"] and len(words) > 1:
            return " ".join(words[:2]), " ".join(words[2:])
        return words[0], " ".join(words[1:])

    def get_current_price(self, car):
        selector = 'div.VechiclePriceItem__priceItemBuy___EbiJT a.VechiclePriceItem__priceItemPrice___rbTmA span.VehicleFormattedPrice__container___NYXO4 span.FormattedNumber__formattedNumber___iNXv2 span'
        elements = car.find_elements(By.CSS_SELECTOR, selector)
        return elements[0].text.strip() if elements else None

    def get_car_data(self, car):
        brand_model = self.get_text_or_none(car, 'h4[class*="VehicleTitle__manufacturerModel"]')
        brand, model = self.extract_brand_model(brand_model)

        props = car.find_elements(By.CSS_SELECTOR, 'div.VehicleProperty__carProp___nBAOW span')
        km = props[0].text.strip() if len(props) > 0 else None
        build_year = props[1].text.strip() if len(props) > 1 else None
        transmission = props[2].text.strip() if len(props) > 2 else None
        fuel = props[3].text.strip() if len(props) > 3 else None
        power = props[4].text.strip() if len(props) > 4 else None
        raw = props[5].text.strip() if len(props) > 5 else None

        consumption = emission = None
        if raw:
            parts = raw.replace("\n", ",").split(",")
            for p in parts:
                p = p.strip()
                if "l/100km" in p:
                    consumption = p
                elif "g CO2/km" in p:
                    emission = p

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
            'CurrentPrice': self.get_current_price(car)
        }

# --- Main Scraper Function ---
def scrape_with_filter(filter_set):
    search_url = build_search_url("https://www.auto.de/search", filter_set)
    print(f"[START] Scraping: {search_url}")

    browser = WebAutomation(headless=False)
    fetcher = CarFetcher(browser.driver)
    all_car_data = []

    try:
        browser.driver.get(search_url)
        browser.accept_cookies()
        browser.zoom_out_css(0.75)

        for page_number in range(1, 31):
            print(f"\n[PAGE {page_number}] Scrolling...")
            browser.slow_scroll()
            cars = browser.driver.find_elements(By.CSS_SELECTOR, 'section.VehicleSmallCard__vehicle____C5Tg')
            print(f"[PAGE {page_number}] Found {len(cars)} car elements on the page.")

            unique_data = set()
            page_results = []

            for car in cars:
                data = fetcher.get_car_data(car)
                if not data:
                    continue
                identifier = normalize_identifier(data)
                if identifier not in unique_data:
                    unique_data.add(identifier)
                    page_results.append(data)
                    print(f"[CAR] {identifier}")

                if len(unique_data) == 15:
                    break

            if len(page_results) == 0:
                print(f"[STOP] Geen nieuwe unieke auto's gevonden op pagina {page_number} → stoppen.")
                break

            all_car_data.extend(page_results)
            print(f"[PAGE {page_number}] Saved {len(page_results)} unique cars.")

            if not browser.go_to_next_page():
                break

    finally:
        browser.quit()

    # ✅ Alleen hier wordt CSV opgeslagen, per filter
    if all_car_data:
        df = pd.DataFrame(all_car_data)
        df.drop_duplicates(subset=['Brand', 'Model', 'Kilometers', 'CurrentPrice'], inplace=True)
        filter_slug = urlencode(filter_set).replace("=", "_").replace("&", "_")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"car_data_{filter_slug}_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"[✓] Data opgeslagen in: {filename}")

    return all_car_data

# --- Parallel Control ---
def scrape_auto_de_parallel():
    filters = [
        {"FIRST_REGISTRATION[from]": "2017", "FIRST_REGISTRATION[to]": "2017"},
        {"FIRST_REGISTRATION[from]": "2018", "FIRST_REGISTRATION[to]": "2018"},
        {"FIRST_REGISTRATION[from]": "2019", "FIRST_REGISTRATION[to]": "2019"},
        {"FIRST_REGISTRATION[from]": "2020", "FIRST_REGISTRATION[to]": "2020"},
        {"FIRST_REGISTRATION[from]": "2021", "FIRST_REGISTRATION[to]": "2021"},
        {"FIRST_REGISTRATION[from]": "2022", "FIRST_REGISTRATION[to]": "2022"},
        {"FIRST_REGISTRATION[from]": "2023", "FIRST_REGISTRATION[to]": "2023"},
        {"FIRST_REGISTRATION[from]": "2024", "FIRST_REGISTRATION[to]": "2024"},
        {"FIRST_REGISTRATION[from]": "2025", "FIRST_REGISTRATION[to]": "2025"},
    ]

    all_data = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(scrape_with_filter, f) for f in filters]
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_data.extend(result)


    # Maak gecombineerde CSV met alles
    if all_data:
        df_all = pd.DataFrame(all_data)
        df_all.drop_duplicates(subset=['Brand', 'Model', 'Kilometers', 'CurrentPrice'], inplace=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        df_all.to_csv(f"car_data_all_combined_{timestamp}.csv", index=False)
        print(f"[✓] Gecombineerde dataset opgeslagen als: car_data_all_combined_{timestamp}.csv")

if __name__ == "__main__":
    scrape_auto_de_parallel()
