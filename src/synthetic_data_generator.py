import numpy as np
import pandas as pd


class SyntheticDataGenerator:
    def __init__(
        self,
        training_df,
        regression_manager,
        thresholds,
        random_seed=42
    ):
        self.training_df = training_df
        self.regression_manager = regression_manager
        self.thresholds = thresholds

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

        self.random_generator = np.random.default_rng(
            random_seed
        )

    def generate(self, number_of_rows=180, interval_seconds=2):
        last_time = self.training_df["sampled_at"].max()

        last_elapsed = self.training_df[
            "elapsed_seconds"
        ].max()

        timestamps = pd.date_range(
            start=last_time + pd.Timedelta(
                seconds=interval_seconds
            ),
            periods=number_of_rows,
            freq=f"{interval_seconds}s"
        )

        elapsed_seconds = (
            last_elapsed
            + np.arange(
                1,
                number_of_rows + 1
            ) * interval_seconds
        )

        synthetic_df = pd.DataFrame({
            "sampled_at": timestamps,
            "elapsed_seconds": elapsed_seconds
        })

        for axis in self.axis_columns:
            model = self.regression_manager.models[axis]

            X_test = synthetic_df[
                ["elapsed_seconds"]
            ]

            predicted_values = model.predict(X_test)

            training_residuals = self.training_df[
                f"{axis}_residual"
            ].dropna().to_numpy()

            sampled_noise = self.random_generator.choice(
                training_residuals,
                size=number_of_rows,
                replace=True
            )

            synthetic_values = (
                predicted_values + sampled_noise
            )

            synthetic_values = np.maximum(
                synthetic_values,
                0
            )

            synthetic_df[axis] = synthetic_values

        return synthetic_df

    def inject_anomaly(
        self,
        dataframe,
        axis,
        start_row,
        number_of_rows,
        event_type
    ):
        result_df = dataframe.copy()

        if axis not in self.axis_columns:
            raise ValueError(f"Unknown axis: {axis}")

        if event_type not in ["ALERT", "ERROR"]:
            raise ValueError(
                "event_type must be either 'ALERT' or 'ERROR'"
            )

        end_row = start_row + number_of_rows

        selected_rows = result_df.iloc[
            start_row:end_row
        ]

        model = self.regression_manager.models[axis]

        X_selected = selected_rows[
            ["elapsed_seconds"]
        ]

        predicted_values = model.predict(X_selected)

        min_c = self.thresholds[axis]["MinC"]
        max_c = self.thresholds[axis]["MaxC"]

        if event_type == "ALERT":
            target_residual = (
                min_c + max_c
            ) / 2

        else:
            target_residual = max_c * 1.20

        result_df.loc[
            selected_rows.index,
            axis
        ] = predicted_values + target_residual

        return result_df