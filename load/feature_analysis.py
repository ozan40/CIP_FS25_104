import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shap

class FeatureImportancePlotter:
    def __init__(self, pipeline, columns_to_encode, columns_to_scale):
        self.pipeline = pipeline
        self.columns_to_encode = columns_to_encode
        self.columns_to_scale = columns_to_scale

    def plot_importance(self, title):
        ohe = self.pipeline.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
        feature_names = list(ohe.get_feature_names_out(self.columns_to_encode)) + self.columns_to_scale
        importances = self.pipeline.named_steps['regressor'].feature_importances_

        df = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values(by='Importance', ascending=False)
        sns.barplot(data=df.head(10), x='Importance', y='Feature', palette='viridis')
        plt.title(f'Top 10 Feature Importances ({title})')
        plt.tight_layout()
        plt.show()

class SHAPExplainer:
    def __init__(self, pipeline, X_test_transformed, feature_names):
        self.pipeline = pipeline
        self.X_test_transformed = X_test_transformed
        self.feature_names = feature_names

    def explain(self):
        model = self.pipeline.named_steps['regressor']
        explainer = shap.Explainer(model)
        shap_values = explainer(self.X_test_transformed[:100])
        shap.summary_plot(shap_values, self.X_test_transformed[:100], feature_names=self.feature_names)
