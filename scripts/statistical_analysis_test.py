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

# 6️⃣ Train-test split and model fitting
# Justification: Train-test split allows unbiased evaluation of model performance
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

# 7️⃣ Predict and evaluate performance
y_pred = pipeline.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"RMSE: {rmse:.2f} L/100km")
print(f"R² Score: {r2:.2f}")

# 8️⃣ Visualization: Actual vs. Predicted
# Justification: Helps assess systematic errors and visual fit of the model
plt.figure(figsize=(8, 5))
plt.scatter(y_test, y_pred, alpha=0.6)
plt.plot([y.min(), y.max()], [y.min(), y.max()], '--r')
plt.xlabel('Actual Consumption (L/100km)')
plt.ylabel('Predicted Consumption (L/100km)')
plt.title('Actual vs. Predicted Consumption')
plt.show()

