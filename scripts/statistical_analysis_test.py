import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Load the data
auto_df = pd.read_csv("../Data/transformed_output.csv", sep=";")

# 1️⃣ Filter rows where Consumption is not null (Target variable)
df_filtered = auto_df[auto_df['Consumption'].notnull()].copy()

# 2️⃣ Feature engineering: calculate car age from YearMonth to numeric value
# Justification: Car age is a relevant factor influencing fuel consumption, often correlating with wear and efficiency
reference_date = pd.to_datetime("2024-01-01")
df_filtered['car_age'] = (reference_date - pd.to_datetime(df_filtered['YearMonth'])).dt.days / 365

# 3️⃣ Select features and target
features = ['Brand', 'Model', 'Kilometer', 'Power_PS', 'Fuel_Type', 'Gear_Type', 'car_age']
target = 'Consumption'

X = df_filtered[features]
y = df_filtered[target]

# 4️⃣ Split into categorical and numeric features for preprocessing
categorical_features = ['Brand', 'Model', 'Fuel_Type', 'Gear_Type']
numeric_features = ['Kilometer', 'Power_PS', 'car_age']

# 5️⃣ Build pipeline with preprocessing and Linear Regression model
# Justification: Pipelines prevent data leakage and ensure reproducibility and cleaner code (source: scikit-learn docs)
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ], remainder='passthrough')

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])
