import pandas as pd


class AlertDetector:
    def __init__(
        self,
        regression_manager,
        thresholds,
        duration_seconds=10
    ):
        if duration_seconds <= 0:
            raise ValueError(
                "duration_seconds must be greater than zero."
            )

        self.regression_manager = regression_manager
        self.thresholds = thresholds
        self.duration_seconds = duration_seconds

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

        self.alert_start_times = {
            axis: None
            for axis in self.axis_columns
        }

        self.error_start_times = {
            axis: None
            for axis in self.axis_columns
        }

        self.alert_logged = {
            axis: False
            for axis in self.axis_columns
        }

        self.error_logged = {
            axis: False
            for axis in self.axis_columns
        }

    def calculate_residual(self, row, axis):
        model = self.regression_manager.models[axis]

        elapsed_seconds = float(
            row["elapsed_seconds"]
        )

        prediction_input = pd.DataFrame({
            "elapsed_seconds": [elapsed_seconds]
        })

        prediction = model.predict(
            prediction_input
        )[0]

        actual = float(row[axis])

        residual = actual - prediction

        return prediction, residual

    def process_row(self, row):
        timestamp = pd.to_datetime(
            row["sampled_at"],
            utc=True
        )

        detected_events = []

        for axis in self.axis_columns:
            prediction, residual = (
                self.calculate_residual(
                    row,
                    axis
                )
            )

            min_c = self.thresholds[axis]["MinC"]
            max_c = self.thresholds[axis]["MaxC"]

            # -------------------------
            # ERROR threshold tracking
            # -------------------------
            if residual >= max_c:

                if self.error_start_times[axis] is None:
                    self.error_start_times[axis] = timestamp

                error_duration = (
                    timestamp
                    - self.error_start_times[axis]
                ).total_seconds()

                if (
                    error_duration >= self.duration_seconds
                    and not self.error_logged[axis]
                ):
                    detected_events.append({
                        "axis": axis,
                        "event_type": "ERROR",
                        "start_time": self.error_start_times[axis],
                        "detected_at": timestamp,
                        "duration_seconds": error_duration,
                        "prediction": prediction,
                        "actual": float(row[axis]),
                        "residual": residual,
                        "threshold": max_c,
                    })

                    self.error_logged[axis] = True

            else:
                self.error_start_times[axis] = None
                self.error_logged[axis] = False

            # -------------------------
            # ALERT threshold tracking
            # -------------------------
            if min_c <= residual < max_c:

                if self.alert_start_times[axis] is None:
                    self.alert_start_times[axis] = timestamp

                alert_duration = (
                    timestamp
                    - self.alert_start_times[axis]
                ).total_seconds()

                if (
                    alert_duration >= self.duration_seconds
                    and not self.alert_logged[axis]
                ):
                    detected_events.append({
                        "axis": axis,
                        "event_type": "ALERT",
                        "start_time": self.alert_start_times[axis],
                        "detected_at": timestamp,
                        "duration_seconds": alert_duration,
                        "prediction": prediction,
                        "actual": float(row[axis]),
                        "residual": residual,
                        "threshold": min_c,
                    })

                    self.alert_logged[axis] = True

            else:
                self.alert_start_times[axis] = None
                self.alert_logged[axis] = False

        return detected_events