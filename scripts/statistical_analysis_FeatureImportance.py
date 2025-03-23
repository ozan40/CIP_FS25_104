import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from sklearn.impute import SimpleImputer
import seaborn as sns

# Load the data
auto_df = pd.read_csv("../Data/transformed_output.csv", sep=";")

# Filter rows where Consumption is not null (Target variable)
df_filtered = auto_df[auto_df['Consumption'].notnull()].copy()

# Feature engineering: calculate car age from YearMonth to numeric value
reference_date = pd.to_datetime("2025-01-01")
df_filtered['car_age'] = (reference_date - pd.to_datetime(df_filtered['YearMonth'])).dt.days / 365
auto_df['car_age'] = (reference_date - pd.to_datetime(auto_df['YearMonth'])).dt.days / 365

# Select features and target
features = ['Brand', 'Model', 'Kilometer', 'Power_PS', 'Fuel_Type', 'Gear_Type', 'car_age']
target = 'Consumption'

X = df_filtered[features]
y = df_filtered[target]

# Split into categorical and numeric features for preprocessing
# categorical_features = ['Brand', 'Model', 'Fuel_Type', 'Gear_Type']
# numeric_features = ['Kilometer', 'Power_PS', 'car_age']

column_types = {
    'Brand':'category',
    'Model':'category',
    'Fuel_Type':'category',
    'Gear_Type':'category',
    'Kilometer':'numeric',
    'Power_PS': 'numeric',
    'car_age':'numeric'
}

columns_to_scale = [key for key in column_types.keys() if column_types[key] == 'numeric']
columns_to_encode = [key for key in column_types.keys() if column_types[key] == 'category']

numeric_transformer = Pipeline(steps=[
    ("imputer",SimpleImputer(strategy='median')),
    ('scaler',StandardScaler())
])

categorical_transformer = Pipeline([
    ("imputer",SimpleImputer(strategy='constant', fill_value = 'missing')),
    ('onehot',OneHotEncoder(handle_unknown = 'ignore'))
])

# Preprocessing pipeline with scaling and encoding
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', categorical_transformer, columns_to_encode),
        ('num', numeric_transformer, columns_to_scale)
    ])

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train and evaluate Random Forest
pipeline_rf = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])
pipeline_rf.fit(X_train, y_train)

param_grid_rf = {
    'regressor__n_estimators': [100, 200],
    'regressor__max_depth': [None, 10, 20],
    'regressor__min_samples_split': [2, 5]
}

# --- Feature Importance from Random Forest ---
# Extract feature names after preprocessing
ohe = pipeline_rf.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
encoded_cat_features = ohe.get_feature_names_out(columns_to_encode)
all_feature_names = np.concatenate([encoded_cat_features, columns_to_scale])

# Extract importances
importances = pipeline_rf.named_steps['regressor'].feature_importances_

# Create DataFrame
feature_importance_df = pd.DataFrame({
    'Feature': all_feature_names,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

# Visualize Top 10 Features
plt.figure(figsize=(10, 6))
sns.barplot(data=feature_importance_df.head(10), x='Importance', y='Feature', palette='viridis')
plt.title('Top 10 Feature Importances (Random Forest)')
plt.tight_layout()
plt.show()

# Interpretation:
# 1. Power_PS (engine power) has the highest importance, indicating it has the strongest influence on fuel consumption.
# 2. car_age (vehicle age) follows, showing older cars typically consume more fuel due to wear and lower efficiency.
# 3. Kilometer (mileage) has moderate importance, reflecting its relation to vehicle wear.
# 4. Fuel_Type (Diesel, Benzin) and specific Models contribute to variance in consumption, but less than technical numeric features.
# Source: Zacharof et al. (2016), European Commission; T&E Report (2018); Scikit-learn feature_importance documentation.

# Note: Feature importances in Random Forest help explain model decisions and can guide feature selection and model interpretability.