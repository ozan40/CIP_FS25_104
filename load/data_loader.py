import pandas as pd

class DataLoader:
    def __init__(self, path):
        self.path = path

    def load_data(self):
        df = pd.read_csv(self.path, sep=';')
        self.ref_date = pd.to_datetime("2025-01-01")
        df['car_age'] = (self.ref_date - pd.to_datetime(df['YearMonth'])).dt.days / 365
        return df

    def prepare_features(self, df):
        df_filtered = df[df['Consumption'].notnull()].copy()
        df_filtered['car_age'] = (self.ref_date - pd.to_datetime(df_filtered['YearMonth'])).dt.days / 365
        features = ['Brand', 'Model','cleaned_Price', 'Kilometer','Fuel_Type', 'Gear_Type',
                    'Power_PS','car_age','CO2_g_km','Fuel_Cost_per_100km',
                    'Annual_Fuel_Cost','CO2_per_year','Marketplace']
        target = 'Consumption'
        return df_filtered[features], df_filtered[target], features