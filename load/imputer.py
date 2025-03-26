class ConsumptionImputer:
    def __init__(self, best_pipeline, features):
        self.pipeline = best_pipeline
        self.features = features

    def impute(self, df):
        missing_df = df[df['Consumption'].isnull()].copy()
        X_missing = missing_df[self.features]
        predictions = self.pipeline.predict(X_missing)
        df.loc[df['Consumption'].isnull(), 'Consumption'] = predictions
        print("Missing values imputed.")
        return df