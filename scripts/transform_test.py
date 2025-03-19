import pandas as pd
import numpy as np

<<<<<<< HEAD
car_df = pd.read_csv('../crawled_output.csv', sep = ";")
=======
car_df = pd.read_csv('../Data/crawled_output.csv', sep =";")
>>>>>>> Ozan
print(car_df.head())

########################################################################################################################
# 🔹 **1) Fehlende Werte (`NaN`) behandeln**
car_df.fillna(value={"Consumption": "0 l/100 km", "CO2_Emission": "0 g/km"}, inplace=True)  # Ersetze leere Werte mit "0"
########################################################################################################################
# 🔹 **2) Strings in numerische Werte umwandeln**
car_df["Kilometer"] = car_df["Kilometer"].str.replace(" km", "").str.replace(".", "").astype(float)
car_df["Power_kW"] = car_df["Horsepower"].str.extract(r"(\d+)").astype(float)  # Extrahiere kW als Zahl
car_df["Consumption"] = car_df["Consumption"].str.replace(" l/100 km", "").str.replace(",", ".").astype(float)
car_df["CO2_Emission"] = car_df["CO2_Emission"].str.replace(" g/km", "").astype(float)
# Datumsformat anpassen
car_df["YearMonth"] = pd.to_datetime(car_df["YearMonth"], format="%m/%Y")

cleaned_prices = []  # Neue Liste für bereinigte Preise

for val in car_df["Price"]:
    if isinstance(val, str):  # Stelle sicher, dass der Wert ein String ist
        cleaned_val = (
            val.replace(".", "")  # Tausenderpunkt entfernen
            .replace(",", "")  # Dezimaltrennzeichen entfernen
            .replace("-", "")  # Eventuelle "-" Zeichen entfernen
            .replace("€", "")  # Euro-Symbol entfernen
            .strip()  # Leerzeichen entfernen
        )

        # Falls der bereinigte Wert eine Zahl ist, konvertieren wir ihn in `int`
        if cleaned_val.isdigit():
            cleaned_prices.append(int(cleaned_val))
        else:
            cleaned_prices.append(np.nan)  # Falls es Text ist, ersetze mit NaN
    else:
        cleaned_prices.append(np.nan)  # Falls kein String, speichere NaN

# Konvertiere die Liste in eine Spalte des DataFrames
car_df["cleaned_Price"] = cleaned_prices
########################################################################################################################
# 🔹 **4) Unlogische Werte entfernen (z. B. falsche Verbrauchswerte)**
car_df = car_df[(car_df["Consumption"] > 0) & (car_df["Consumption"] < 50)]  # Verbrauch zwischen 0 und 50 l/100 km

# 🔹 **5) Outlier-Erkennung für Kilometerstand**
# q1 = car_df["Kilometer"].quantile(0.05)  # Unteres 5%-Quantil
# q3 = car_df["Kilometer"].quantile(0.95)  # Oberes 95%-Quantil
# df = car_df[(car_df["Kilometer"] >= q1) & (car_df["Kilometer"] <= q3)]  # Entferne extreme Werte

####################################################################################################
# 🔹 **6) Neue Spalte hinzufügen: Preis pro Kilometer**
car_df["Price_per_km"] = car_df["cleaned_Price"] / car_df["Kilometer"]

# 1️⃣ Fuel_Cost_per_100km: Kraftstoffkosten pro 100 km berechnen
# Jeder Treibstofftyp hat einen Durchschnittspreis.
# Durchschnittliche Kraftstoffpreise (kann angepasst werden)

# Quelle Benzin und Diesel: https://www.swr.de/swraktuell/diesel-und-benzinpreise-aktuell-so-tanken-sie-heute-clever-100.html#:~:text=In%20Deutschland%20kostet%20ein%20Liter,M%C3%A4rz%202025%20um%2019%20Uhr.
# Quelle Elektro: https://www.adac.de/rund-ums-fahrzeug/auto-kaufen-verkaufen/autokosten/elektroauto-kostenvergleich/
# Quelle CNG: https://www.adac.de/verkehr/tanken-kraftstoff-antrieb/alternative-antriebe/erdgas/
# Quelle LPG: https://www.da-direkt.de/elektroauto-versicherung/ratgeber/autogas-lpg
fuel_prices = {
    "Benzin": 1.77, "Diesel": 1.65, "Elektro": 0.414, "Autogas (LPG)": 0.229,
    "Erdgas (CNG)": 1.20, "Elektro/Benzin": 1.50, "Elektro/Diesel": 1.40
}

# Berechnung: Verbrauch * Treibstoffpreis
car_df["Fuel_Cost_per_100km"] = car_df.apply(lambda row: row["Consumption"] * fuel_prices.get(row["Fuel_Type"], np.nan), axis=1)

# 2️⃣ Annual_Fuel_Cost: Jährliche Spritkosten basierend auf 11.500 miles/Jahr = 18507.456 km/jahr
# https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle#:~:text=typical%20passenger%20vehicle%3F-,A%20typical%20passenger%20vehicle%20emits%20about%204.6%20metric%20tons%20of,8%2C887%20grams%20of%20CO2.
# Viele Fahrer fahren 18507.456 km/Jahr.
car_df["Annual_Fuel_Cost"] = car_df["Fuel_Cost_per_100km"] * (18507.456 / 100 )

# 3️⃣ CO2_per_km berechnen
# Die CO₂-Emissionen sind in g/km gespeichert.
# https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle#:~:text=typical%20passenger%20vehicle%3F-,A%20typical%20passenger%20vehicle%20emits%20about%204.6%20metric%20tons%20of,8%2C887%20grams%20of%20CO2.
car_df["CO2_per_year"] = car_df["CO2_Emission"] * (18507.456 / 1000) # in kg
average_co2_per_year = 4600 # 4.6 metric tons (4600 kg)

# 🔥 **Kategorie basierend auf dem Vergleich mit dem Durchschnitt erstellen**
def categorize_co2_emission(co2_value):
    return "Above Average" if co2_value > average_co2_per_year else "Below Average"

# 🏷 **Kategorie-Spalte hinzufügen**
car_df["CO2_Emission_Category"] = car_df["CO2_per_year"].apply(categorize_co2_emission)

# ✅ **Ergebnis ausgeben**
print(car_df[car_df["CO2_Emission_Category"] == 'Above Average'])
####################################################################################################

# 🔹 **7) Getriebearten vereinheitlichen**
car_df["Gear_Type"] = car_df["Gear_Type"].replace({"Halbautomatik": "Automatik"})

# 🔹 **8) Spaltennamen standardisieren**
car_df.rename(columns={"CO2_Emission": "CO2_g_km"}, inplace=True)

# 🔹 **Ergebnis anzeigen**
print(car_df.dtypes)  # Prüfe, ob alles korrekt konvertiert wurde
print(car_df.head())  # Überprüfe das Endergebnis
