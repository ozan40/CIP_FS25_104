from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class ModelTrainer:
    def __init__(self, X, y, preprocessor):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)
        self.preprocessor = preprocessor
        self.models = {}
        self.trained_pipelines = {}
        self.results_before = {}
        self.results_after = {}

    def add_model(self, name, regressor, param_grid, color):
        pipeline = Pipeline([
            ('preprocessor', self.preprocessor),
            ('regressor', regressor)
        ])
        self.models[name] = {
            'pipeline': pipeline,
            'param_grid': param_grid,
            'color': color
        }

    def train_and_evaluate(self, name):
        model_data = self.models[name]
        pipeline = model_data['pipeline']
        pipeline.fit(self.X_train, self.y_train)

        y_pred = pipeline.predict(self.X_test)
        rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
        r2 = r2_score(self.y_test, y_pred)
        self.results_before[name] = (rmse, r2)

        print(f"\n{name} Before Tuning:")
        print(f"RMSE: {rmse:.2f}, R²: {r2:.2f}")

        return pipeline

    def tune_model(self, name):
        model_data = self.models[name]
        pipeline = model_data['pipeline']
        param_grid = model_data['param_grid']

        y_pred_before = pipeline.predict(self.X_test)
        rmse_before = np.sqrt(mean_squared_error(self.y_test, y_pred_before))
        r2_before = r2_score(self.y_test, y_pred_before)

        grid_search = GridSearchCV(pipeline, param_grid, cv=3,
                                   scoring='neg_root_mean_squared_error', n_jobs=-1)
        grid_search.fit(self.X_train, self.y_train)

        print(f"\n{name} Best Parameters:")
        print(grid_search.best_params_)

        best_model = grid_search.best_estimator_
        y_pred_after = best_model.predict(self.X_test)
        rmse_after = np.sqrt(mean_squared_error(self.y_test, y_pred_after))
        r2_after = r2_score(self.y_test, y_pred_after)

        if rmse_after < rmse_before:
            print(f"{name} Tuned Model Retained.")
            self.results_after[name] = (rmse_after, r2_after)
            self.trained_pipelines[name] = best_model
        else:
            print(f"{name} Original Model Retained.")
            self.results_after[name] = (rmse_before, r2_before)
            self.trained_pipelines[name] = pipeline

    def train_all(self):
        for name in self.models:
            self.train_and_evaluate(name)
            self.tune_model(name)

    def plot_results(self, after_tuning=True):
        results = self.results_after if after_tuning else self.results_before
        x = np.arange(len(results))
        width = 0.35

        model_names = list(results.keys())
        rmse_scores = [v[0] for v in results.values()]
        r2_scores = [v[1] for v in results.values()]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width/2, rmse_scores, width, label='RMSE', color='skyblue')
        ax.bar(x + width/2, r2_scores, width, label='R² Score', color='lightgreen')

        ax.set_xlabel('Models')
        ax.set_ylabel('Metric Value')
        ax.set_title('Model Comparison ' + ('After Tuning' if after_tuning else 'Before Tuning'))
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, rotation=45)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        for idx, bar in enumerate(ax.patches):
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom')

        plt.tight_layout()
        plt.show()
