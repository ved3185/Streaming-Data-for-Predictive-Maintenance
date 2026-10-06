import json
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template


class WebDashboard:
    def __init__(self):
        self.app = Flask(__name__)

        self.project_root = (
            Path(__file__)
            .resolve()
            .parents[1]
        )

        self.data_folder = (
            self.project_root
            / "data"
        )

        self.dashboard_data_path = (
            self.data_folder
            / "dashboard_data.csv"
        )

        self.events_path = (
            self.data_folder
            / "events_log.csv"
        )

        self.thresholds_path = (
            self.data_folder
            / "thresholds.json"
        )

        self.register_routes()

    def load_dashboard_data(self):
        dataframe = pd.read_csv(
            self.dashboard_data_path
        )

        events_df = pd.read_csv(
            self.events_path
        )

        with open(
            self.thresholds_path,
            "r"
        ) as file:
            thresholds = json.load(file)

        return (
            dataframe,
            events_df,
            thresholds
        )

    def register_routes(self):

        @self.app.route("/")
        def dashboard():
            return render_template(
                "dashboard.html"
            )

        @self.app.route("/api/dashboard-data")
        def dashboard_data():

            (
                dataframe,
                events_df,
                thresholds
            ) = self.load_dashboard_data()

            axis_columns = [
                "axis_1",
                "axis_2",
                "axis_3",
                "axis_4",
                "axis_5",
                "axis_6",
                "axis_7",
                "axis_8",
            ]

            axes = {}

            for axis in axis_columns:

                predicted_column = (
                    f"{axis}_predicted"
                )

                min_c = float(
                    thresholds[axis]["MinC"]
                )

                max_c = float(
                    thresholds[axis]["MaxC"]
                )

                actual = (
                    dataframe[axis]
                    .astype(float)
                    .tolist()
                )

                predicted = (
                    dataframe[
                        predicted_column
                    ]
                    .astype(float)
                    .tolist()
                )

                alert_boundary = [
                    prediction + min_c
                    for prediction in predicted
                ]

                error_boundary = [
                    prediction + max_c
                    for prediction in predicted
                ]

                axes[axis] = {
                    "actual": actual,
                    "predicted": predicted,
                    "alert_boundary": alert_boundary,
                    "error_boundary": error_boundary,
                }

            alert_count = int(
                (
                    events_df["event_type"]
                    == "ALERT"
                ).sum()
            )

            error_count = int(
                (
                    events_df["event_type"]
                    == "ERROR"
                ).sum()
            )

            if error_count > 0:
                highest_severity = "ERROR"

            elif alert_count > 0:
                highest_severity = "ALERT"

            else:
                highest_severity = "NORMAL"

            return jsonify({
                "timestamps": (
                    dataframe["sampled_at"]
                    .astype(str)
                    .tolist()
                ),

                "axes": axes,

                "thresholds": thresholds,

                "events": (
                    events_df
                    .fillna("")
                    .to_dict(
                        orient="records"
                    )
                ),

                "summary": {
                    "highest_severity": highest_severity,
                    "alerts": alert_count,
                    "errors": error_count,
                    "rows": len(dataframe),
                }
            })

    def run(self):
        self.app.run(
            debug=False
        )


if __name__ == "__main__":
    dashboard = WebDashboard()
    dashboard.run()