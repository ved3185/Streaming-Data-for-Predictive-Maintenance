import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler


class DataPreprocessor:
    def __init__(self):
        self.axis_columns = [
            "axis_1",
            "axis_2",
            "axis_3",
            "axis_4",
            "axis_5",
            "axis_6",
            "axis_7",
            "axis_8",
        ]

        self.minmax_scaler = MinMaxScaler()
        self.standard_scaler = StandardScaler()

        self.is_fitted = False

    def fit_on_training_data(self, training_df):
        self.minmax_scaler.fit(
            training_df[self.axis_columns]
        )

        self.standard_scaler.fit(
            training_df[self.axis_columns]
        )

        self.is_fitted = True

    def transform_test_data(self, test_df):
        if not self.is_fitted:
            raise RuntimeError(
                "Scalers must be fitted on training data first."
            )

        processed_df = test_df.copy()

        normalized_values = self.minmax_scaler.transform(
            test_df[self.axis_columns]
        )

        standardized_values = self.standard_scaler.transform(
            test_df[self.axis_columns]
        )

        for index, axis in enumerate(self.axis_columns):
            processed_df[f"{axis}_normalized"] = (
                normalized_values[:, index]
            )

            processed_df[f"{axis}_standardized"] = (
                standardized_values[:, index]
            )

        return processed_df