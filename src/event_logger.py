from pathlib import Path

import pandas as pd


class EventLogger:
    def __init__(self, log_path):
        self.log_path = Path(log_path)

    def save_events(self, events):
        events_df = pd.DataFrame(events)

        if events_df.empty:
            print("No events were detected.")
            return events_df

        self.log_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        events_df.to_csv(
            self.log_path,
            index=False
        )

        print(
            f"{len(events_df)} events saved to "
            f"{self.log_path}"
        )

        return events_df