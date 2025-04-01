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
    # Plot 3: Fuel Consumption
    plt.figure(figsize=(8, 5))
    sns.barplot(data=fuel_emissions, x='Marketplace', y='Consumption')
    plt.title('Average Fuel Consumption (L/100km) by Marketplace')
    plt.ylabel('Fuel Consumption (L/100km)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Plot 4: CO2 Emissions
    plt.figure(figsize=(8, 5))
    sns.barplot(data=fuel_emissions, x='Marketplace', y='CO2_g_km')
    plt.title('Average CO₂ Emissions (g/km) by Marketplace')
    plt.ylabel('CO₂ Emissions (g/km)')
    plt.xticks(rotation=45)
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
            'regressor__alpha': [0.001, 0.01, 0.1, 1.0]
        },
        "gray"
    )

    # Add Random Forest Regression incl. parameter tuning
    trainer.add_model(
        "Random Forest", RandomForestRegressor(n_estimators = 100, random_state = 42),
        {
            'regressor__n_estimators': [100, 200, 300],  # Number of trees in the forest
            'regressor__max_depth': [None, 10, 20, 30],  # Max depth of each tree
            'regressor__min_samples_split': [2, 5, 10],  # Minimum samples required to split a node
            'regressor__min_samples_leaf': [1, 2, 4],  # Minimum samples at a leaf node
            'regressor__max_features': ['auto', 'sqrt', 'log2'],  # Number of features considered at each split
            'regressor__bootstrap': [True, False]  # Whether bootstrap samples are used
        },
        'green'
    )

    # Add Random Forest Regression incl. parameter tuning
    trainer.add_model(
        "KNN", KNeighborsRegressor(),
        {
            'regressor__n_neighbors': [3, 5, 10],
            'regressor__weights': ['uniform', 'distance']
        },
        "brown"
    )

    # add Gradient Boosting incl. parameter tuning
    trainer.add_model(
        "Gradient Boosting", GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42),
        {
            'regressor__n_estimators': [100, 200, 300],  # Number of boosting stages
            'regressor__learning_rate': [0.01, 0.05, 0.1],  # Shrinks contribution of each tree
            'regressor__max_depth': [3, 5, 7, 11],  # Max depth of individual trees
            'regressor__max_features': ['auto', 'sqrt', 'log2']  # Features considered per split
        },
        'orange'
    )

    # add SVR incl. parameter tuning
    trainer.add_model(
        "SVR", SVR(),
        {
            'regressor__kernel': ['rbf', 'linear'],  # Kernel types: radial basis function & linear
            'regressor__C': [0.1, 1, 10],  # Regularization parameter
            'regressor__epsilon': [0.01, 0.1, 0.2],  # Tolerance for error margin
            'regressor__gamma': ['scale', 'auto']  # Kernel coefficient
        },
        "darkred"
    )

    # add XGBoost incl. parameter tuning
    trainer.add_model(
        "XGBoost", XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, verbosity=0),
        {
            'regressor__n_estimators': [100, 200],
            'regressor__learning_rate': [0.05, 0.1],
            'regressor__max_depth': [3, 5, 7, 11],
            'regressor__gamma': [0, 0.1, 0.2],                  # Minimum loss reduction for split
            'regressor__reg_alpha': [0, 0.1, 1],                # L1 regularization term
            'regressor__reg_lambda': [1, 1.5, 2]                # L2 regularization term
        },
        "purple"
    )

    trainer.add_model(
        "MLP Regressor", MLPRegressor(max_iter=500, random_state=42),
        {
            'regressor__hidden_layer_sizes': [(100,), (50, 50), (100, 50, 25)],  # Architecture (layers and neurons)
            'regressor__activation': ['relu', 'tanh'],  # Activation functions
            'regressor__solver': ['adam', 'sgd'],  # Optimization algorithm
            'regressor__learning_rate': ['constant', 'adaptive'],  # Learning rate schedule
            'regressor__early_stopping': [True]  # To avoid overfitting
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

#    imputed_df.to_csv("Data/imputed_output.csv", sep = ";")