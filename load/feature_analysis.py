# feature_analysis.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from sklearn.metrics import mean_squared_error, r2_score


class FeatureImportanceAnalyzer:
    def __init__(self, best_model_name, best_pipeline, columns_to_encode, columns_to_scale):
        self.best_model_name = best_model_name
        self.pipeline = best_pipeline
        self.columns_to_encode = columns_to_encode
        self.columns_to_scale = columns_to_scale
        self.feature_names = self._get_feature_names()

    def _get_feature_names(self):
        """Extract final feature names after preprocessing."""
        ohe = self.pipeline.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
        encoded_cat_features = ohe.get_feature_names_out(self.columns_to_encode)
        return list(encoded_cat_features) + self.columns_to_scale

    def plot_feature_importance(self, top_n=10):
        """Plot feature importances for tree-based models (e.g. RandomForest, XGBoost)."""
        model = self.pipeline.named_steps['regressor']
        if not hasattr(model, 'feature_importances_'):
            raise ValueError(f"Model {self.best_model_name} does not support feature_importances_.")

        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': importances
        }).sort_values(by='Importance', ascending=False)

        plt.figure(figsize=(10, 6))
        sns.barplot(data=importance_df.head(top_n), x='Importance', y='Feature', palette='viridis')
        plt.title(f'Top {top_n} Feature Importances ({self.best_model_name})')
        plt.tight_layout()
        plt.show()

    def evaluate_best_model(self, X_sample, y_sample):
        """
        Evaluates the best model using residual analysis.
        """
        try:
            # Vorhersage
            y_pred = self.pipeline.predict(X_sample)
            residuals = y_sample - y_pred

            # RMSE berechnen
            rmse = np.sqrt(mean_squared_error(y_sample, y_pred))
            r2 = r2_score(y_sample, y_pred)

            # Residual Plot
            plt.figure(figsize=(6, 5))
            plt.scatter(y_pred, residuals, alpha=0.6, color='cornflowerblue', edgecolor='k')
            plt.axhline(y=0, color='red', linestyle='--', linewidth=2)
            plt.xlabel("Predicted Consumption (L/100km)")
            plt.ylabel("Residuals")
            plt.title(f"Residual Plot ({self.best_model_name})")
            plt.grid(True)
            plt.tight_layout()
            plt.show()

            print(f"{self.best_model_name} - RMSE: {rmse:.4f}, R²: {r2:.4f}")

        except Exception as e:
            print(f"Evaluation of best model failed: {e}")