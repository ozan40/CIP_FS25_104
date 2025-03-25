import pandas as pd

class DataLoader:
    def __init__(self, path):
        self.path = path

    def load_data(self):
        df = pd.read_csv(self.path, sep=';')
        ref_date = pd.to_datetime("2025-01-01")
        df['car_age'] = (ref_date - pd.to_datetime(df['YearMonth'])).dt.days / 365
        return df

    def prepare_features(self, df):
        df_filtered = df[df['Consumption'].notnull()].copy()
        features = ['Brand', 'Model', 'Kilometer', 'Power_PS', 'Fuel_Type', 'Gear_Type', 'car_age']
        target = 'Consumption'
        return df_filtered[features], df_filtered[target], features