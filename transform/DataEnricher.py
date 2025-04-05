import pandas as pd
import numpy as np
import re

class DataEnricher:
    def __init__(self, df):
        self.df = df

    def enrich_data(self):
        # Preis pro Kilometer berechnen
        self.df["Price_per_km"] = self.df["cleaned_Price"] / self.df["Kilometer"]
        if 'Marketplace' in self.df.columns:
            if self.df['Marketplace'].iloc[0] == 'Autoscout24.de':
                self.df['Brand'] = self.df['Brand'].str.replace('SEAT', 'Seat')
        try:
            # Kraftstoffpreise definieren
            # Quellen:
            # Benzin/Diesel: SWR (https://www.swr.de/swraktuell/diesel-und-benzinpreise-aktuell)
            # Elektro: ADAC (https://www.adac.de/rund-ums-fahrzeug/auto-kaufen-verkaufen/autokosten/elektroauto-kostenvergleich/)
            # LPG/CNG: DA Direkt (https://www.da-direkt.de/elektroauto-versicherung/ratgeber/autogas-lpg)
            # Wasserstoff: https://emcel.com/de/kosten-von-wasserstoff/

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

            # Quelle: EPA - https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle

            self.df["CO2_per_year"] = round(self.df["CO2_Emission"] * (18507.456 / 1000),2)
            average_co2_per_year = 4600  # 4.6 metric tons (4600 kg)

            # CO2-Kategorie bestimmen
            self.df["CO2_Emission_Category"] = self.df["CO2_per_year"].apply(
                lambda co2_value: "Above Average" if co2_value > average_co2_per_year else "Below Average"
            )

            # Getriebearten vereinheitlichen
            self.df["Gear_Type"] = self.df["Gear_Type"].replace({"Halbautomatik": "Automatik"})


        except KeyError:
            if 'Marketplace' in self.df.columns:
                if self.df['Marketplace'].iloc[0] == 'Auto.de':
                    fuel_prices_auto_de = {
                        "Benzin": 1.77, "Diesel": 1.65, "Elektro": 0.414, "Autogas": 0.229,
                        "Erdgas": 1.20, "Hybrid (Elektro / Benzin)": 1.50, "Keine Information": 0, "Wasserstoff": 7.0
                    }

                    # Kraftstoffkosten pro 100 km berechnen
                    self.df["Fuel_Cost_per_100km"] = self.df.apply(
                        lambda row: row["Consumption"] * fuel_prices_auto_de.get(row["Fuel"], np.nan), axis=1
                        )

                    # Jährliche Spritkosten basierend auf 18.507 km/Jahr
                    self.df["Annual_Fuel_Cost"] = round(self.df["Fuel_Cost_per_100km"] * (18507.456 / 100), 2)

                    # CO2-Emissionen pro Jahr berechnen
                    self.df["CO2_per_year"] = round(self.df["CO2_Emission"] * (18507.456 / 1000), 2)
                    average_co2_per_year = 4600  # 4.6 metric tons (4600 kg)
                    # CO2-Kategorie bestimmen
                    self.df["CO2_Emission_Category"] = self.df["CO2_per_year"].apply(
                        lambda co2_value: "Above Average" if co2_value > average_co2_per_year else "Below Average"
                    )
                    self.df['Gear_Type'] = self.df['Transmission'].str.replace('Manuell', 'Schaltgetriebe')
                    self.df['Fuel_Type'] = (self.df['Fuel'].str.replace('Hybrid (Elektro / Benzin)', 'Elektro/Benzin').
                                            str.replace('Autogas', 'Autogas (LPG)').str.replace('Erdgas','Erdgas (CNG)'))

                elif self.df['Marketplace'].iloc[0] == "Mobile.de":
                    fuel_prices_mobile_de = {
                        "Benzin": 1.77, "Diesel": 1.65, "Elektro": 0.414, "Andere": 1.00,
                        "Erdgas (CNG)": 1.20, "Hybrid (Benzin/Elektro)": 1.50, "Keine Information": 0
                    }
                    if self.df["Consumption"].isna().any():
                        self.df["Fuel_Cost_per_100km"] = np.nan
                    else:
                    # Kraftstoffkosten pro 100 km berechnen
                        self.df["Fuel_Cost_per_100km"] = self.df.apply(
                            lambda row: row["Consumption"] * fuel_prices_mobile_de.get(row["Fuel_Type"], np.nan), axis=1
                        )

                    if self.df["CO2_Emission"].isna().any():
                        # Falls np.nan, setze alle Berechnungen auf np.nan
                        self.df["Annual_Fuel_Cost"] = np.nan
                        self.df["CO2_per_year"] = np.nan
                        self.df["CO2_Emission_Category"] = np.nan
                    else:
                        # Jährliche Spritkosten basierend auf 18.507 km/Jahr
                        self.df["Annual_Fuel_Cost"] = round(self.df["Fuel_Cost_per_100km"] * (18507.456 / 100), 2)

                        # CO2-Emissionen pro Jahr berechnen
                        self.df["CO2_per_year"] = round(self.df["CO2_Emission"] * (18507.456 / 1000), 2)

                        # Durchschnittliche CO2-Emissionen pro Jahr (in kg)
                        average_co2_per_year = 4600  # 4.6 metric tons (4600 kg)

                        # CO2-Kategorie bestimmen
                        self.df["CO2_Emission_Category"] = self.df["CO2_per_year"].apply(
                            lambda co2_value: "Above Average" if co2_value > average_co2_per_year else "Below Average"
                        )

                    self.df['Fuel_Type'] = (self.df['Fuel_Type'].str.replace('Hybrid (Benzin/Elektro)', 'Elektro/Benzin').
                                            str.replace('Andere', 'Sonstige'))
                    self.df['Price_Eval'] = (self.df['Price_Eval'].str.replace('Ohne Bewertung', 'Keine Information'))
                    # Spaltennamen standardisieren
        self.df.rename(columns={"CO2_Emission": "CO2_g_km"}, inplace=True)


        return self.df

    def select_columns(self):
        self.df_0 = DataEnricher.enrich_data(self)
        self.df_2 = self.df_0[['Brand','Model','YearMonth','cleaned_Price',
                               'Kilometer','Gear_Type','Fuel_Type','Consumption',
                               'CO2_g_km', 'Power_PS', 'Price_per_km','Fuel_Cost_per_100km','Annual_Fuel_Cost',
                               'CO2_per_year','CO2_Emission_Category','Marketplace']]
        return self.df_2

    def categorize_cols(self):

        self.enriched_df = DataEnricher.select_columns(self)

        try:
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
        except KeyError:
            if 'Marketplace' in self.df.columns:
                if self.df['Marketplace'].iloc[0] == 'Auto.de':
                    # handle categorical data
                    ordered_cats_auto_de = {
                        'Gear_Type': ['Keine Information', 'Schaltgetriebe', 'Automatik'],
                        'Fuel_Type': ['Keine Information', 'Wasserstoff', 'Autogas (LPG)', 'Erdgas (CNG)', 'Elektro/Benzin',
                                      'Diesel', 'Benzin']
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
                        elif col in ordered_cats_auto_de.keys():
                            category = pd.CategoricalDtype(ordered_cats_auto_de[col], ordered=True)
                            self.enriched_df[col] = self.enriched_df[col].astype(category)

                elif self.df['Marketplace'].iloc[0] == 'Mobile.de':
                    # handle categorical data
                    ordered_cats_mobile_de = {
                        'Price_Eval': ['Keine Information','Hoher Preis', 'Erhöhter Preis', 'Fairer Preis', 'Guter Preis',
                                       'Sehr guter Preis'],
                        'Fuel_Type': ['Keine Information', 'Sonstige', 'Erdgas (CNG)', 'Elektro/Benzin','Diesel', 'Benzin']
                    }

                    # Loop through DataFrame columns to efficiently change data types
                    for col in self.enriched_df:



                        # Convert columns containing ordered categorical data to ordered categories using dict
                        if col in ordered_cats_mobile_de.keys():
                            category = pd.CategoricalDtype(ordered_cats_mobile_de[col], ordered=True)
                            self.enriched_df[col] = self.enriched_df[col].astype(category)

        return self.enriched_df