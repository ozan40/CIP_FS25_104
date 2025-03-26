import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shap

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

    def shap_analysis(self, X_sample):
        """Run SHAP analysis for models like XGBoost."""
        model = self.pipeline.named_steps['regressor']
        preprocessor = self.pipeline.named_steps['preprocessor']
        X_transformed = preprocessor.transform(X_sample)

        try:
            explainer = shap.Explainer(model)
            shap_values = explainer(X_transformed[:100])
            shap.summary_plot(shap_values, X_transformed[:100], feature_names=self.feature_names)
        except Exception as e:
            print(f"SHAP analysis failed: {e}")