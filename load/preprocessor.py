from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

class PreprocessorBuilder:
    def __init__(self, features, target,column_types):
        self.features = features
        self.target = target
        self.column_types = column_types

    def build_pipeline(self):
        columns_to_scale = [k for k, v in self.column_types.items() if v == 'numeric']
        columns_to_encode = [k for k, v in self.column_types.items() if v == 'category']

        numeric_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        categorical_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        preprocessor = ColumnTransformer([
            ('cat', categorical_transformer, columns_to_encode),
            ('num', numeric_transformer, columns_to_scale)
        ])
        return preprocessor, columns_to_encode, columns_to_scale
