from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Lasso, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from sklearn.svm import SVR
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import load


if __name__ == "__main__":


    # Load data
    file_path = "Data/transformed_output.csv"
    df = pd.read_csv(file_path, sep=';')

    # Prepare style
    sns.set(style="whitegrid")

    # Define threshold for grouping less frequent brands
    brand_counts = df['Brand'].value_counts()
    top_brands = brand_counts[brand_counts > 100].index  # Keep brands with >100 listings
    df['Brand_Grouped'] = df['Brand'].apply(lambda x: x if x in top_brands else 'Other')

    # -----------------------
    # Research Question 1
    # -----------------------

    # Average price per grouped brand and marketplace
    avg_price = (
        df.groupby(['Marketplace', 'Brand_Grouped'])['cleaned_Price']
        .mean()
        .reset_index()
    )
    print("######################### Research Question 1 #########################\n")
    # Plot 1: Average Used Car Price
    plt.figure(figsize=(14, 6))
    sns.barplot(data=avg_price, x='Brand_Grouped', y='cleaned_Price', hue='Marketplace')
    plt.title('Average Used Car Price by Brand Group and Marketplace')
    plt.ylabel('Average Price (€)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Average price per km
    avg_price_per_km = (
        df.groupby(['Marketplace', 'Brand_Grouped'])['Price_per_km']
        .mean()
        .reset_index()
    )

    # Plot 2: Price per Kilometer
    plt.figure(figsize=(14, 6))
    sns.barplot(data=avg_price_per_km, x='Brand_Grouped', y='Price_per_km', hue='Marketplace')
    plt.title('Average Price per Kilometer by Brand Group and Marketplace')
    plt.ylabel('€/km')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Durchschnittlicher Verbrauch pro Marke & Marketplace
    avg_consumption = (
        df.groupby(['Marketplace', 'Brand_Grouped'])['Consumption']
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(14, 6))
    sns.barplot(data=avg_consumption, x='Brand_Grouped', y='Consumption', hue='Marketplace')
    plt.title('Average Fuel Consumption by Brand Group and Marketplace')
    plt.ylabel('Consumption (L/100km)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # -----------------------
    # Research Question 2
    # -----------------------

    # Average fuel consumption and CO₂ emissions per marketplace
    fuel_emissions = (
        df.groupby('Marketplace')[['Consumption', 'CO2_g_km']]
        .mean()
        .reset_index()
    )
    print("######################### Research Question 2 #########################\n")

    # Durchschnittlicher Verbrauch & Emissionen nach Marketplace + Fuel_Type
    fuel_emissions_by_type = (
        df.groupby(['Marketplace', 'Fuel_Type'])[['Consumption', 'CO2_g_km']]
        .mean()
        .reset_index()
    )

    # Set plot style
    sns.set(style="whitegrid")

    # Plot 3: Average Fuel Consumption by Fuel Type and Marketplace
    plt.figure(figsize=(12, 6))
    sns.barplot(data=fuel_emissions_by_type, x='Fuel_Type', y='Consumption', hue='Marketplace')
    plt.title('Average Fuel Consumption (L/100km) by Fuel Type and Marketplace')
    plt.ylabel('Fuel Consumption (L/100km)')
    plt.xlabel('Fuel Type')
    plt.tight_layout()
    plt.show()

    # Plot 4: Average CO₂ Emissions by Fuel Type and Marketplace
    plt.figure(figsize=(12, 6))
    sns.barplot(data=fuel_emissions_by_type, x='Fuel_Type', y='CO2_g_km', hue='Marketplace')
    plt.title('Average CO2 Emissions (g/km) by Fuel Type and Marketplace')
    plt.ylabel('CO₂ Emissions (g/km)')
    plt.xlabel('Fuel Type')
    plt.tight_layout()
    plt.show()

    print("######################### Research Question 3 #########################\n")
    # calling DataLoader classes
    data_loader = load.DataLoader("Data/transformed_output.csv")
    data_frame = data_loader.load_data()
    X, y, features = data_loader.prepare_features(data_frame)

    # calling PreprocessBuilder classes to build preprocessor
    builder = load.PreprocessorBuilder(X,features,y)
    preprocessor, columns_to_encode, columns_to_scale = builder.build_pipeline()

    # calling ModelTrainer() classes to build and train models
    trainer = load.ModelTrainer(X, y, preprocessor)

    # get train and testdata
    X_train, X_test, y_train, y_test = trainer.get_train_test_data()

    # Add Ridge Regression incl. parameter tuning
    trainer.add_model(
        "Ridge Regression", Ridge(),
        {
            'regressor__alpha': [0.1, 1.0, 10.0]
        },
        "blue"
    )

    # Add Lasso Regression incl. parameter tuning
    trainer.add_model(
        "Lasso", Lasso(),
        {
            'regressor__alpha': [0.01, 0.1, 1.0]
        },
        "gray"
    )

    # Add Random Forest Regression incl. parameter tuning
    trainer.add_model(
        "Random Forest", RandomForestRegressor(random_state=42),
        {
            'regressor__n_estimators': [100, 300],  # Fixierte Baumanzahl
            'regressor__max_depth': [10, 20],
            'regressor__min_samples_split': [2, 5]
        },
        "green"
    )
    # Add KNN Regressor incl. parameter tuning
    trainer.add_model(
        "KNN", KNeighborsRegressor(),
        {
            'regressor__n_neighbors': [3, 7],
            'regressor__weights': ['uniform']
        },
        "brown"
    )

    # add Gradient Boosting incl. parameter tuning
    trainer.add_model(
        "Gradient Boosting", GradientBoostingRegressor(random_state=42),
        {
            'regressor__n_estimators': [100],
            'regressor__learning_rate': [0.05, 0.1],
            'regressor__max_depth': [3, 5]
        },
        "orange"
    )

    # add SVR incl. parameter tuning
    trainer.add_model(
        "SVR", SVR(),
        {
            'regressor__kernel': ['rbf'],
            'regressor__C': [1, 10],
            'regressor__epsilon': [0.1]
        },
        "darkred"
    )

    # add XGBoost incl. parameter tuning
    trainer.add_model(
        "XGBoost", XGBRegressor(random_state=42, verbosity=0),
        {
            'regressor__n_estimators': [100, 300],
            'regressor__max_depth': [3, 5, 7, 11, 13],
            'regressor__learning_rate': [0.005, 0.05, 0.5]
        },
        "purple"
    )

    # add MLP Regressor incl. parameter tuning
    trainer.add_model(
        "MLP Regressor", MLPRegressor(max_iter=500, random_state=42),
        {
            'regressor__hidden_layer_sizes': [(100,), (50, 50)],
            'regressor__activation': ['relu'],
            'regressor__solver': ['adam']
        },
        "cyan"
    )

    # train and tune all models
    trainer.train_all()

    # visualisation
    trainer.plot_results(after_tuning = False)
    trainer.plot_results(after_tuning = True)

    # get best_model_name and best_pipeline
    best_model_name, best_pipeline = trainer.get_best_model()

    # calling FeatureImportancePlotter to plot results
    analyzer = load.FeatureImportanceAnalyzer(best_model_name, best_pipeline, columns_to_encode, columns_to_scale)
    analyzer.plot_feature_importance()
    analyzer.shap_analysis(X_test)

    # Calling ConsumptionImputer class
    imputer = load.ConsumptionImputer(best_pipeline, features)
    imputed_df = imputer.impute(data_frame)

    imputed_df.to_csv("Data/imputed_output.csv", sep = ";")
    print("######################### Imputed Output #########################\n")
    # Average fuel consumption and CO₂ emissions per marketplace


    # Durchschnittlicher Verbrauch & Emissionen nach Marketplace + Fuel_Type
    fuel_emissions_by_type_after_imputing = (
        imputed_df.groupby(['Marketplace', 'Fuel_Type'])[['Consumption', 'CO2_g_km']]
        .mean()
        .reset_index()
    )

    # Set plot style
    sns.set(style="whitegrid")

    # Plot 3: Average Fuel Consumption by Fuel Type and Marketplace
    plt.figure(figsize=(12, 6))
    sns.barplot(data=fuel_emissions_by_type_after_imputing, x='Fuel_Type', y='Consumption', hue='Marketplace')
    plt.title('Average Fuel Consumption (L/100km) by Fuel Type and Marketplace')
    plt.ylabel('Fuel Consumption (L/100km)')
    plt.xlabel('Fuel Type')
    plt.tight_layout()
    plt.show()