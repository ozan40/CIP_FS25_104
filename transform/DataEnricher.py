import pandas as pd
import numpy as np

class DataEnricher:
    def __init__(self, df):
        self.df = df

    def enrich_data(self):
        # Preis pro Kilometer berechnen
        self.df["Price_per_km"] = self.df["cleaned_Price"] / self.df["Kilometer"]

        # Kraftstoffpreise definieren
        fuel_prices = {
            "Benzin": 1.77, "Diesel": 1.65, "Elektro": 0.414, "Autogas (LPG)": 0.229,
            "Erdgas (CNG)": 1.20, "Elektro/Benzin": 1.50, "Elektro/Diesel": 1.40
        }

        # Kraftstoffkosten pro 100 km berechnen
        self.df["Fuel_Cost_per_100km"] = self.df.apply(
            lambda row: row["Consumption"] * fuel_prices.get(row["Fuel_Type"], np.nan), axis=1
        )

        # Jährliche Spritkosten basierend auf 18.507 km/Jahr
        self.df["Annual_Fuel_Cost"] = round(self.df["Fuel_Cost_per_100km"] * (18507.456 / 100),2)

        # CO2-Emissionen pro Jahr berechnen
        self.df["CO2_per_year"] = round(self.df["CO2_Emission"] * (18507.456 / 1000),2)
        average_co2_per_year = 4600  # 4.6 metric tons (4600 kg)

        # CO2-Kategorie bestimmen
        self.df["CO2_Emission_Category"] = self.df["CO2_per_year"].apply(
            lambda co2_value: "Above Average" if co2_value > average_co2_per_year else "Below Average"
        )

        # Getriebearten vereinheitlichen
        self.df["Gear_Type"] = self.df["Gear_Type"].replace({"Halbautomatik": "Automatik"})

        # Spaltennamen standardisieren
        self.df.rename(columns={"CO2_Emission": "CO2_g_km"}, inplace=True)

        return self.df

    def select_columns(self):
        self.df_0 = DataEnricher.enrich_data(self)
        self.df_2 = self.df_0[['Brand','Model','YearMonth','cleaned_Price','Price_Eval',
                               'Kilometer','Gear_Type','Fuel_Type','Consumption',
                               'CO2_g_km', 'Power_PS', 'Price_per_km','Fuel_Cost_per_100km','Annual_Fuel_Cost',
                               'CO2_per_year','CO2_Emission_Category']]
        return self.df_2

    def categorize_cols(self):

        self.enriched_df = DataEnricher.select_columns(self)
        # Create a dictionary of columns containing ordered categorical data
        ordered_cats = {
            'Price_Eval': ['Keine Information', 'Erhöhter Preis', 'Fairer Preis', 'Guter Preis', 'Sehr guter Preis'],
            'Gear_Type': ['Keine Information', 'Schaltgetriebe', 'Automatik'],
            'Fuel_Type': ['Keine Information', 'Sonstige', 'Autogas (LPG)', 'Erdgas (CNG)', 'Diesel', 'Benzin']
        }

        two_factor_cats = {
            'CO2_Emission_Category': {'Above Average': False, 'Below Average': True}
        }

        # Loop through DataFrame columns to efficiently change data types
        for col in self.enriched_df:

            # Convert two-factor categories to bool
            if col in ['CO2_Emission_Category']:
                self.enriched_df[col] = self.enriched_df[col].map(two_factor_cats[col])


            # Convert columns containing ordered categorical data to ordered categories using dict
            elif col in ordered_cats.keys():
                category = pd.CategoricalDtype(ordered_cats[col], ordered=True)
                self.enriched_df[col] = self.enriched_df[col].astype(category)

        return self.enriched_df

