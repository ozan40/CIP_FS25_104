import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, KFold
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, make_scorer
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


# Store performance results
model_results_before_tuning = {}
model_results_after_tuning = {}

# Function to evaluate model
def evaluate_model(name, pipeline, X_test, y_test, color):
    y_pred = pipeline.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    model_results_before_tuning[name] = (rmse, r2)
    print(f"\n{name} Results:")
    print(f"RMSE: {rmse:.2f} L/100km")
    print(f"R² Score: {r2:.2f}")
    # plt.figure(figsize=(8, 5))
    # plt.scatter(y_test, y_pred, alpha=0.6, color=color)
    # plt.plot([y.min(), y.max()], [y.min(), y.max()], '--r')
    # plt.xlabel('Actual Consumption (L/100km)')
    # plt.ylabel('Predicted Consumption (L/100km)')
    # plt.title(f'{name}: Actual vs. Predicted Consumption')
    # plt.show()

# Function for hyperparameter tuning with result comparison
def tune_and_evaluate_model(name, pipeline, param_grid, X_train, X_test, y_train, y_test, color):
    # Evaluate before tuning
    y_pred_before = pipeline.predict(X_test)
    rmse_before = np.sqrt(mean_squared_error(y_test, y_pred_before))
    r2_before = r2_score(y_test, y_pred_before)

    print(f"\n{name} Before Tuning:")
    print(f"RMSE: {rmse_before:.2f} L/100km, R²: {r2_before:.2f}")

    # Grid Search
    grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='neg_root_mean_squared_error', n_jobs=-1)
    grid_search.fit(X_train, y_train)

    print(f"Best Parameters ({name}):")
    print(grid_search.best_params_)

    # Evaluate after tuning
    y_pred_after = grid_search.predict(X_test)
    rmse_after = np.sqrt(mean_squared_error(y_test, y_pred_after))
    r2_after = r2_score(y_test, y_pred_after)

    print(f"{name} After Tuning:")
    print(f"RMSE: {rmse_after:.2f} L/100km, R²: {r2_after:.2f}")

    # Compare and select best
    if rmse_after < rmse_before:
        print(f"{name}: Tuned model retained.")
        model_results_after_tuning[name] = (rmse_after, r2_after)
        y_pred = y_pred_after
    else:
        print(f"{name}: Original model retained (better performance).")
        model_results_after_tuning[name] = (rmse_before, r2_before)
        y_pred = y_pred_before

    # # Visualize
    # plt.figure(figsize=(8, 5))
    # plt.scatter(y_test, y_pred, alpha=0.6, color=color)
    # plt.plot([y.min(), y.max()], [y.min(), y.max()], '--r')
    # plt.xlabel('Actual Consumption (L/100km)')
    # plt.ylabel('Predicted Consumption (L/100km)')
    # plt.title(f'{name} (Final): Actual vs. Predicted Consumption')
    # plt.show()

    # # Visualize
    # plt.figure(figsize=(8, 5))
    # plt.scatter(y_test, y_pred, alpha=0.6, color=color)
    # plt.plot([y.min(), y.max()], [y.min(), y.max()], '--r')
    # plt.xlabel('Actual Consumption (L/100km)')
    # plt.ylabel('Predicted Consumption (L/100km)')
    # plt.title(f'{name} (Final): Actual vs. Predicted Consumption')
    # plt.show()




# Train and evaluate Linear Regression
pipeline_ridge = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', Ridge())
])
pipeline_ridge.fit(X_train, y_train)
evaluate_model("Ridge Regression", pipeline_ridge, X_test, y_test, 'blue')
param_grid_ridge = {
    'regressor__alpha': [0.1, 1.0, 10.0]
}
tune_and_evaluate_model("Ridge Regression", pipeline_ridge, param_grid_ridge, X_train, X_test, y_train, y_test, 'blue')

# Train and evaluate Random Forest
pipeline_rf = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])
pipeline_rf.fit(X_train, y_train)
evaluate_model("Random Forest", pipeline_rf, X_test, y_test, 'green')
param_grid_rf = {
    'regressor__n_estimators': [100, 200, 300],                   # Number of trees in the forest
    'regressor__max_depth': [None, 10, 20, 30],                   # Max depth of each tree
    'regressor__min_samples_split': [2, 5, 10],                   # Minimum samples required to split a node
    'regressor__min_samples_leaf': [1, 2, 4],                     # Minimum samples at a leaf node
    'regressor__max_features': ['auto', 'sqrt', 'log2'],         # Number of features considered at each split
    'regressor__bootstrap': [True, False]                         # Whether bootstrap samples are used
}
tune_and_evaluate_model("Random Forest", pipeline_rf, param_grid_rf, X_train, X_test, y_train, y_test, 'green')

# Train and evaluate Gradient Boosting
pipeline_gb = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42))
])
pipeline_gb.fit(X_train, y_train)
evaluate_model("Gradient Boosting", pipeline_gb, X_test, y_test, 'orange')
param_grid_gb = {
    'regressor__n_estimators': [100, 200, 300],         # Number of boosting stages
    'regressor__learning_rate': [0.01, 0.05, 0.1],      # Shrinks contribution of each tree
    'regressor__max_depth': [3, 5, 7, 11],                  # Max depth of individual trees
    'regressor__max_features': ['auto', 'sqrt', 'log2'] # Features considered per split
}
tune_and_evaluate_model("Gradient Boosting", pipeline_gb, param_grid_gb, X_train, X_test, y_train, y_test, 'orange')

# Train and evaluate XGBoost
pipeline_xgb = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, verbosity=0))
])
pipeline_xgb.fit(X_train, y_train)
evaluate_model("XGBoost", pipeline_xgb, X_test, y_test, 'purple')
param_grid_xgb = {
    'regressor__n_estimators': [100, 200],
    'regressor__learning_rate': [0.05, 0.1],
    'regressor__max_depth': [3, 5, 7, 11],
    'regressor__gamma': [0, 0.1, 0.2],                  # Minimum loss reduction for split
    'regressor__reg_alpha': [0, 0.1, 1],                # L1 regularization term
    'regressor__reg_lambda': [1, 1.5, 2]                # L2 regularization term
}

tune_and_evaluate_model("XGBoost", pipeline_xgb, param_grid_xgb, X_train, X_test, y_train, y_test, 'purple')

# Train and evaluate MLP Regressor
pipeline_mlp = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', MLPRegressor(max_iter=500, random_state=42))
])
pipeline_mlp.fit(X_train, y_train)
evaluate_model("MLP Regressor", pipeline_mlp, X_test, y_test, 'cyan')
param_grid_mlp = {
    'regressor__hidden_layer_sizes': [(100,), (50, 50), (100, 50, 25)],       # Architecture (layers and neurons)
    'regressor__activation': ['relu', 'tanh'],          # Activation functions
    'regressor__solver': ['adam','sgd'],                             # Optimization algorithm
    'regressor__learning_rate': ['constant','adaptive'],              # Learning rate schedule
    'regressor__early_stopping': [True]                                # To avoid overfitting
}
tune_and_evaluate_model("MLP Regressor", pipeline_mlp, param_grid_mlp, X_train, X_test, y_train, y_test, 'cyan')

# Final Model Comparison Before Tuning Summary
print("\nFinal Model Comparison Summary Before Tuning:")
for model_name, (rmse, r2) in model_results_before_tuning.items():
    print(f"{model_name}: RMSE = {rmse:.2f}, R² = {r2:.2f}")

# Combined Visual Comparison
x = np.arange(len(model_results_before_tuning))
width = 0.35
model_names = list(model_results_before_tuning.keys())
rmse_scores_before = [v[0] for v in model_results_before_tuning.values()]
r2_scores_before = [v[1] for v in model_results_before_tuning.values()]

fig, ax = plt.subplots(figsize=(12, 6))
rmse_bars_before = ax.bar(x - width/2, rmse_scores_before, width, label='RMSE', color='skyblue')
r2_bars_before = ax.bar(x + width/2, r2_scores_before, width, label='R² Score', color='lightgreen')

ax.set_xlabel('Models')
ax.set_ylabel('Metric Value')
ax.set_title('Model Comparison Before Tuning: RMSE and R² Score')
ax.set_xticks(x)
ax.set_xticklabels(model_names, rotation=45)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.legend()

for bar in rmse_bars_before:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

for bar in r2_bars_before:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

plt.tight_layout()
plt.show()


# Final Model Comparison After Tuning Summary
print("\nFinal Model Comparison Summary After Tuning:")
for model_name, (rmse, r2) in model_results_after_tuning.items():
    print(f"{model_name}: RMSE = {rmse:.2f}, R² = {r2:.2f}")

# Combined Visual Comparison
x = np.arange(len(model_results_after_tuning))
width = 0.35
model_names = list(model_results_after_tuning.keys())
rmse_scores_after = [v[0] for v in model_results_after_tuning.values()]
r2_scores_after = [v[1] for v in model_results_after_tuning.values()]

fig, ax = plt.subplots(figsize=(12, 6))
rmse_bars_after = ax.bar(x - width/2, rmse_scores_after, width, label='RMSE', color='skyblue')
r2_bars_after = ax.bar(x + width/2, r2_scores_after, width, label='R² Score', color='lightgreen')

ax.set_xlabel('Models')
ax.set_ylabel('Metric Value')
ax.set_title('Model Comparison After Tuning: RMSE and R² Score')
ax.set_xticks(x)
ax.set_xticklabels(model_names, rotation=45)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.legend()

for bar in rmse_bars_after:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

for bar in r2_bars_after:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

plt.tight_layout()
plt.show()

print(model_results_after_tuning)

# Recommendation: Use the best model (lowest RMSE, highest R²) for imputing missing Consumption values.

trained_pipelines = {
    'Ridge Regression': pipeline_ridge,
    'Random Forest': pipeline_rf,
    'Gradient Boosting': pipeline_gb,
    'XGBoost': pipeline_xgb,
    'MLP Regressor': pipeline_mlp
}

def impute_missing_consumption(df, model_results, trained_pipelines):
    df_missing = df[df['Consumption'].isnull()].copy()
    X_missing_raw = df_missing[features]

    # Impute missing values in X_missing if any
    # Explanation: Why SimpleImputer was necessary:
    # Before predicting the missing "Consumption" values, the features (X_missing) may contain NaNs in columns such as "Power_PS" or "Kilometer".
    # Many models like MLPRegressor, Ridge, and RandomForest do not support NaNs in the input data.
    # SimpleImputer fills these NaNs (in numeric features) with the mean of each column, ensuring clean data.
    # This allows models to make valid predictions without errors, enabling us to impute the missing target values (Consumption).
    # Reference: https://scikit-learn.org/stable/modules/impute.html


    X_missing = df_missing[features]

    sorted_models = sorted(model_results.items(), key=lambda x: (x[1][0], -x[1][1]))
    best_model_name = sorted_models[0][0]

    best_pipeline = trained_pipelines[best_model_name]

    predicted_consumption = best_pipeline.predict(X_missing)
    df.loc[df['Consumption'].isnull(), 'Consumption'] = predicted_consumption

    print(f"Missing Consumption values imputed using {best_model_name}.")
    return df

# Apply the function
df_imputed = impute_missing_consumption(auto_df, model_results_after_tuning, trained_pipelines)

# Save completed dataset
# df_imputed.to_csv("../Data/imputed_output.csv", sep=";", index=False)
# print("Imputed dataset saved to 'imputed_output.csv'.")
#######################################################################################################################
# Model Comparison: Before and After Hyperparameter Tuning
# Plot 1: Model Performance Before Tuning
# This plot shows the performance of five different models before any optimization:
#
# Random Forest and XGBoost already show strong performance with low RMSE (0.31 and 0.51 respectively) and high R² scores (0.96 and 0.88).
#
# Ridge Regression and Gradient Boosting have higher RMSE values (0.67 and 0.71) and lower R² scores (0.80 and 0.78),
# suggesting underfitting or less flexibility in modeling the data.
#
# The MLP Regressor is in the mid-range, performing better than Ridge but worse than tree-based models.
#
# Interpretation:
# Tree-based models, especially Random Forest and XGBoost, handle non-linearities and feature interactions more effectively,
# which explains their superior performance even before tuning. Reference: [Hastie et al., 2009 – "The Elements of Statistical Learning"].
#
# Plot 2: Model Performance After Tuning
# After applying GridSearchCV and hyperparameter tuning:
#
# XGBoost improves to RMSE 0.26 and R² 0.97, becoming the best overall model.
#
# Random Forest also improves slightly to RMSE 0.28, R² 0.97, closely following XGBoost.
#
# Gradient Boosting shows improvement but remains behind (RMSE 0.31, R² 0.96).
#
# MLP Regressor shows marginal improvement and remains less competitive (RMSE 0.55, R² 0.86).
#
# Ridge Regression does not improve after tuning, confirming its limited capacity for modeling complex relationships.
#
# Conclusion:
# Hyperparameter tuning significantly enhanced model performance, especially for XGBoost and Gradient Boosting,
# confirming the value of model optimization. The reduction in RMSE and increase in R² indicate better prediction accuracy and fit to the data.
#
# Transition to Feature Importance Analysis
# Given the strong performance of XGBoost and Random Forest, we now shift our focus to understanding why these models perform well.
#
# ➡️ Both models allow extraction of feature importances, which help explain which features most influence the prediction of fuel consumption.
# Understanding feature contributions supports interpretability, transparency,
# and trust in model predictions – especially important in real-world applications (e.g., automotive efficiency, policy decisions).
#
# We will now explore feature importance and SHAP values to analyze the internal decision logic of XGBoost and
# Random Forest, following best practices in explainable AI.
# Reference: Lundberg & Lee (2017), "A Unified Approach to Interpreting Model Predictions"; Breiman (2001), "Random Forests".
#
# Let’s dive into feature importance analysis.
########################################################################################################################


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



