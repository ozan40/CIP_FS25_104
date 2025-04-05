import pandas as pd
import numpy as np
import missingno as msno
import matplotlib.pyplot as plt

class DataCleaner:
    def __init__(self, df):
        self.df = df

    def define_datatype(self):
        # clean values with appropriate data types
        try:
            self.df["Kilometer"] = self.df["Kilometer"].str.replace(" km", "").str.replace(".", "").astype(float)
            self.df["Power_PS"] = self.df["Horsepower"].str.extract(r"\((\d+)\s*PS\)").astype(float)
            self.df["Consumption"] = self.df["Consumption"].str.replace(" l/100 km", "").str.replace(",", ".").astype(
                float)
            self.df["CO2_Emission"] = self.df["CO2_Emission"].str.replace(" g/km", "").astype(float)
            self.df["YearMonth"] = pd.to_datetime(self.df["YearMonth"], format="%m/%Y")
        except KeyError:
            # Wenn bestimmte Spalten fehlen, versuche es mit anderen DataFrames
            if "Kilometers" in self.df.columns:
                # Transmission: 'Manuell' -> 'Schaltgetriebe', Automatik bleibt gleich
                self.df["Marketplace"] = "Auto.de"
                self.df["Kilometer"] = self.df["Kilometers"].str.replace(" km", "").str.replace(".", "").astype(float)
                self.df["YearMonth"] = pd.to_datetime(self.df["BuildYear"], format="%m/%Y")

                # Power: '130 kW (177 PS)' -> 177
                self.df['Power_PS'] = self.df['Power'].str.extract(r'\((\d+)\s*PS\)').astype(float)

                # Consumption: '7l/100km' -> 7
                self.df['Consumption'] = self.df['l/Km'].str.extract(r'(\d+)', expand=False).astype(float)

                # CO2: '108g CO2/km (komb)*' -> 108
                self.df['CO2_Emission'] = self.df['Emission'].str.extract(r'(\d+)', expand=False).astype(int)
            elif "brand" in self.df.columns:
                self.df["Marketplace"] = "Mobile.de"
                self.df["Brand"] = self.df["brand"]
                self.df["Model"] = self.df["model"]
                self.df["Kilometer"] = self.df["kilometer"]
                self.df["Gear_Type"] = self.df["gear"]
                self.df["Fuel_Type"] = self.df["fuel"]
                self.df['Price_Eval'] = self.df['price_evaluation']
                self.df["YearMonth"] = pd.to_datetime(self.df["date"], format="%m/%Y")

                # Power: '130 kW (177 PS)' -> 177
                self.df['Power_PS'] = self.df['power']

                # Consumption: '7l/100km' -> 7
                self.df['Consumption'] = self.df['consumption']

                # CO2: '108g CO2/km (komb)*' -> 108
                self.df['CO2_Emission'] = self.df['co2']
            else:
                raise KeyError("None of the expected columns are found in the DataFrame.")

        # Clean Prices
        cleaned_prices = []
        try:
            for val in self.df["Price"]:
                if isinstance(val, str):
                    cleaned_val = (
                        val.replace(".", "")
                        .replace(",", "")
                        .replace("-", "")
                        .replace("€", "")
                        .strip()
                    )
                    cleaned_prices.append(int(cleaned_val) if cleaned_val.isdigit() else np.nan)
                else:
                    cleaned_prices.append(np.nan)
            self.df["cleaned_Price"] = cleaned_prices
        except KeyError:
            if 'CurrentPrice' in self.df.columns:
                self.df['cleaned_Price'] = self.df['CurrentPrice'].astype(str).str.replace('.', '', regex=False).astype(
                    int)
            elif 'price' in self.df.columns:
                self.df['cleaned_Price'] = self.df['price']
            else:
                raise KeyError("No valid price column found for cleaning.")

        return self.df



    def cleaned_categorical_values(self):
        self.cleaned_df = DataCleaner.define_datatype(self)

        try:
            categorical_col = ['Price_Eval','Gear_Type','Fuel_Type']
            self.cleaned_df[categorical_col] = self.cleaned_df[categorical_col].fillna("Keine Information")
        except KeyError:
            # clean categorical data
            categorical_col = ['Transmission', 'Fuel']
            self.df[categorical_col] = self.df[categorical_col].fillna("Keine Information")

        return self.cleaned_df


    def missing_values(self, data):
        self.missing_values = data.isna().sum()
        msno.matrix(data)
        self.plot = plt.show()
        return self.missing_values, self.plot

    def detect_outliers(self):
        """ Berechnet Outlier-Grenzen basierend auf den 2.5%- und 97.5%-Quantilen. """

        outlier_ranges = {}
        numeric_cols = ["Kilometer", "Power_PS", "Consumption", "CO2_Emission", "cleaned_Price"]

        for col in numeric_cols:
            lower_bound = self.df[col].quantile(0.05)  # 2.5%-Quantil
            upper_bound = self.df[col].quantile(0.95)  # 97.5%-Quantil

            outlier_ranges[col] = (lower_bound, upper_bound)
            print(f"Outlier-Bereich für {col}: <= {lower_bound:.2f} & >= {upper_bound:.2f}")



        return outlier_ranges
