import pandas as pd
import numpy as np
import missingno as msno
import matplotlib.pyplot as plt

class DataCleaner:
    def __init__(self, df):
        self.df = df

    def define_datatype(self):
        # clean values with appropriate data types
        self.df["Kilometer"] = self.df["Kilometer"].str.replace(" km", "").str.replace(".", "").astype(float)
        self.df["Power_PS"] = self.df["Horsepower"].str.extract(r"\((\d+)\s*PS\)").astype(float)
        self.df["Consumption"] = self.df["Consumption"].str.replace(" l/100 km", "").str.replace(",", ".").astype(float)
        self.df["CO2_Emission"] = self.df["CO2_Emission"].str.replace(" g/km", "").astype(float)
        self.df["YearMonth"] = pd.to_datetime(self.df["YearMonth"], format="%m/%Y")


        # Clean Prices
        cleaned_prices = []
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

        return self.df



    def cleaned_categorical_values(self):
        self.cleaned_df = DataCleaner.define_datatype(self)

        categorical_col = ['Price_Eval','Gear_Type','Fuel_Type']
        self.cleaned_df[categorical_col] = self.cleaned_df[categorical_col].fillna("Keine Information")

        return self.cleaned_df


    def missing_values(self, df):
        self.missing_values = df.isna().sum()
        msno.matrix(df)
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
