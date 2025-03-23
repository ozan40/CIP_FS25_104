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
    'regressor__n_estimators': [100, 200],
    'regressor__max_depth': [None, 10, 20],
    'regressor__min_samples_split': [2, 5]
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
    'regressor__n_estimators': [100, 200],
    'regressor__learning_rate': [0.05, 0.1],
    'regressor__max_depth': [3, 5]
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
    'regressor__max_depth': [3, 5]
}
tune_and_evaluate_model("XGBoost", pipeline_xgb, param_grid_xgb, X_train, X_test, y_train, y_test, 'purple')

# Train and evaluate MLP Regressor
pipeline_mlp = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000,
                               random_state=42, early_stopping=True))
])
pipeline_mlp.fit(X_train, y_train)
evaluate_model("MLP Regressor", pipeline_mlp, X_test, y_test, 'cyan')
param_grid_mlp = {
    'regressor__hidden_layer_sizes': [(100,), (50, 50)],
    'regressor__alpha': [0.0001, 0.001],
    'regressor__learning_rate_init': [0.001, 0.01]
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
df_imputed.to_csv("../Data/imputed_output.csv", sep=";", index=False)
print("Imputed dataset saved to 'imputed_output.csv'.")









