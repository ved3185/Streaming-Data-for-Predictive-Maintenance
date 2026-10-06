import time
from pathlib import Path

import pandas as pd


class StreamSimulator:
    def __init__(
        self,
        csv_path,
        interval_seconds=2.0
    ):
        if interval_seconds < 0:
            raise ValueError(
                "interval_seconds cannot be negative."
            )

        self.csv_path = Path(csv_path)
        self.interval_seconds = interval_seconds
        self.rows_delivered = 0

    def stream_to_database(
        self,
        database_manager
    ):
        reader = pd.read_csv(
            self.csv_path,
            chunksize=1
        )

        previous_delivery_time = None
        delivery_times = []

        for chunk in reader:

            if previous_delivery_time is not None:
                elapsed = (
                    time.monotonic()
                    - previous_delivery_time
                )

                remaining_wait = (
                    self.interval_seconds
                    - elapsed
                )

                if remaining_wait > 0:
                    time.sleep(remaining_wait)

            row = chunk.iloc[0].to_dict()

            database_manager.insert_streaming_row(
                row
            )

            current_delivery_time = time.monotonic()

            delivery_times.append(
                current_delivery_time
            )

            previous_delivery_time = (
                current_delivery_time
            )

            self.rows_delivered += 1

            if (
                self.rows_delivered % 20 == 0
                or self.rows_delivered == 1
            ):
                print(
                    f"Streamed "
                    f"{self.rows_delivered} rows..."
                )

        return delivery_times

    def stream_rows(self):
        reader = pd.read_csv(
            self.csv_path,
            chunksize=1
        )

        previous_delivery_time = None

        self.rows_delivered = 0

        for chunk in reader:

            if previous_delivery_time is not None:
                elapsed = (
                    time.monotonic()
                    - previous_delivery_time
                )

                remaining_wait = (
                    self.interval_seconds
                    - elapsed
                )

                if remaining_wait > 0:
                    time.sleep(remaining_wait)

            row = chunk.iloc[0].to_dict()

            current_delivery_time = time.monotonic()

            previous_delivery_time = (
                current_delivery_time
            )

            self.rows_delivered += 1

            yield row, current_delivery_time