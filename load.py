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


import load


if __name__ == "__main__":
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
    analyzer.plot_feature_importance(X_test)

    # Calling ConsumptionImputer class
    imputer = load.ConsumptionImputer(best_pipeline, features)
    imputed_df = imputer.impute(data_frame)
    
    imputed_df.to_csv("Data/imputed_output.csv", sep = ";")