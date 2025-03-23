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
import shap

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

# Train and evaluate XGBoost
pipeline_xgb = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, verbosity=0))
])
pipeline_xgb.fit(X_train, y_train)

param_grid_xgb = {
    'regressor__n_estimators': [100, 200],
    'regressor__learning_rate': [0.05, 0.1],
    'regressor__max_depth': [3, 5]
}

# --- Feature Importance from Random Forest ---
# Extract feature names after preprocessing
ohe = pipeline_xgb.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
encoded_cat_features = ohe.get_feature_names_out(columns_to_encode)
all_feature_names = np.concatenate([encoded_cat_features, columns_to_scale])
# 1. Extrahiere One-Hot-Encoded Feature-Namen
ohe_feature_names = pipeline_xgb.named_steps['preprocessor'] \
    .named_transformers_['cat'] \
    .named_steps['onehot'] \
    .get_feature_names_out(columns_to_encode)

# 2. Kombiniere mit numerischen Features (die nur skaliert wurden)
preprocessed_feature_names = list(ohe_feature_names) + columns_to_scale

# Extract importances
importances = pipeline_xgb.named_steps['regressor'].feature_importances_

# Create DataFrame
feature_importance_df_xgb = pd.DataFrame({
    'Feature': all_feature_names,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

# Visualize Top 10 Features
plt.figure(figsize=(10, 6))
sns.barplot(data=feature_importance_df_xgb.head(10), x='Importance', y='Feature', palette='viridis')
plt.title('Top 10 Feature Importances (XGBoost)')
plt.tight_layout()
plt.show()

# Interpretation (XGBoost Feature Importances):
# 1. The most influential feature is Model_218, followed by other specific vehicle models (Model_118, Model_116).
#    → This suggests that particular car models significantly influence fuel consumption predictions.
# 2. Power_PS and Fuel_Type_Diesel are also important, indicating that engine power and fuel type (Diesel) are critical factors.
# 3. Brand_Land Rover and Model_Sprinter indicate brand/model-specific consumption trends.
# 4. car_age and Kilometer are present but less influential than in Random Forest, showing XGBoost relies more on categorical encodings.
#
# Reasoning:
# - XGBoost can capture complex interactions between categorical variables (e.g., Model, Brand) and numerical ones.
# - Feature importance in XGBoost is calculated based on the number of times a feature is used to split the data across all trees, weighted by the improvement in performance.
#
# Reference: Chen & Guestrin (2016), XGBoost: A Scalable Tree Boosting System; https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRegressor.feature_importances_


# SHAP für XGBoost
# Hintergrund: SHAP (SHapley Additive exPlanations) quantifiziert den Beitrag jedes Features zur Vorhersage.
# Quelle: Lundberg & Lee (2017). A Unified Approach to Interpreting Model Predictions.

# 1. Datentransformation durch den Preprocessor (ohne Target-Spalte)
X_transformed = preprocessor.transform(X_test)

# 2. Zugriff auf das trainierte XGBoost Modell
xgb_model = pipeline_xgb.named_steps['regressor']

# 3. SHAP-Explainer initialisieren (TreeExplainer ideal für XGBoost)
explainer = shap.Explainer(xgb_model)

# 4. SHAP-Werte berechnen (einige Stichproben für Performance)
shap_values = explainer(X_transformed[:100])

# 5. SHAP Summary Plot anzeigen (wichtigste Features visuell darstellen)
shap.summary_plot(shap_values, X_transformed[:100], feature_names=preprocessed_feature_names)

# SHAP Interpretation for XGBoost:
# - Power_PS (engine power) shows the highest SHAP impact, indicating a strong influence on the predicted fuel consumption.
#   Higher Power_PS values generally increase fuel consumption (SHAP value > 0).
# - Fuel_Type_Diesel and Fuel_Type_Benzin significantly influence the model’s output.
#   Diesel vehicles tend to have negative SHAP values, indicating lower predicted consumption, aligning with known fuel efficiency trends.
# - car_age and Kilometer show moderate influence.
#   Older cars (high car_age) and higher mileage (Kilometer) are linked to higher consumption predictions.
# - Model and Brand features (e.g., Model_Ranger, Brand_BMW) also contribute but with varied influence depending on vehicle type.

# Reasoning:
# SHAP values help interpret the contribution of each feature to individual predictions, ensuring model transparency.
# Unlike feature_importance in Random Forest/XGBoost, SHAP captures both feature importance and direction (positive/negative impact).
# Reference: Lundberg & Lee (2017), "A Unified Approach to Interpreting Model Predictions" (https://arxiv.org/abs/1705.07874)
# Benefit: SHAP plots validate feature importances seen in other models (e.g., Random Forest), increasing confidence in model insights.



# Train and evaluate MLP Regressor
pipeline_mlp = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=4000,
                               random_state=42, early_stopping=True))
])
pipeline_mlp.fit(X_train, y_train)


# Vorhersagen für Testdaten
y_pred_mlp = pipeline_mlp.predict(X_test)
residuals = y_test - y_pred_mlp  # Residuen = Ist - Vorhersage

# Plot: Residuen vs. Vorhersage
plt.figure(figsize=(10, 6))
sns.scatterplot(x=y_pred_mlp, y=residuals, alpha=0.6)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel('Predicted Consumption (L/100km)')
plt.ylabel('Residuals')
plt.title('Residual Plot: MLP Regressor')
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()

# Interpretation:
# - Die Residuen sind zufällig um die Nulllinie verteilt, ohne sichtbare Muster oder systematische Abweichungen.
# - Dies deutet darauf hin, dass der MLP Regressor keine gravierenden systematischen Fehler macht (kein Overfitting oder Underfitting sichtbar).
# - Die Streuung der Residuen bleibt über den gesamten Vorhersagebereich konstant – ein Hinweis auf homoskedastische Fehler (gleichmäßige Varianz).
# - Einige Ausreißer sind sichtbar, jedoch in akzeptablem Rahmen.

# Fazit:
# Die Residualverteilung zeigt, dass das Modell stabil arbeitet und keine Verzerrung der Vorhersagen aufweist.

# Quelle: Géron, A. (2019). Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow.
# Residual Analysis: https://scikit-learn.org/stable/auto_examples/miscellaneous/plot_residuals.html
