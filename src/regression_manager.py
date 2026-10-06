import pandas as pd
from sklearn.linear_model import LinearRegression


class RegressionManager:
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

        self.models = {}
        self.model_information = {}

    def train_models(self, dataframe, time_column="elapsed_seconds"):
        X = dataframe[[time_column]]

        for axis in self.axis_columns:
            y = dataframe[axis]

            model = LinearRegression()
            model.fit(X, y)

            self.models[axis] = model

            self.model_information[axis] = {
                "slope": model.coef_[0],
                "intercept": model.intercept_,
            }

        return self.model_information

    def add_predictions_and_residuals(
        self,
        dataframe,
        time_column="elapsed_seconds"
    ):
        result_df = dataframe.copy()

        X = result_df[[time_column]]

        for axis in self.axis_columns:
            model = self.models[axis]

            prediction_column = f"{axis}_predicted"
            residual_column = f"{axis}_residual"

            result_df[prediction_column] = model.predict(X)

            result_df[residual_column] = (
                result_df[axis]
                - result_df[prediction_column]
            )

        return result_df

    def get_model_summary(self):
        return pd.DataFrame.from_dict(
            self.model_information,
            orient="index"
        )

    def get_residual_summary(self, dataframe):
        summary = []

        for axis in self.axis_columns:
            residual_column = f"{axis}_residual"

            residuals = dataframe[residual_column]

            positive_residuals = residuals[residuals > 0]

            summary.append({
                "axis": axis,
                "mean_residual": residuals.mean(),
                "std_residual": residuals.std(),
                "max_residual": residuals.max(),
                "positive_95th_percentile": positive_residuals.quantile(0.95),
                "positive_99th_percentile": positive_residuals.quantile(0.99),
            })

        return pd.DataFrame(summary)