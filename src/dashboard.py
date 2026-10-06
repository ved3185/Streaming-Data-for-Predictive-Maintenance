import pandas as pd
import matplotlib.pyplot as plt


class MaintenanceDashboard:
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

    def create_dashboard(
        self,
        dataframe,
        events_df,
        thresholds,
        save_path=None
    ):
        dashboard_df = dataframe.copy()

        dashboard_df["sampled_at"] = pd.to_datetime(
            dashboard_df["sampled_at"],
            utc=True
        )

        events_copy = events_df.copy()

        if not events_copy.empty:
            events_copy["start_time"] = pd.to_datetime(
                events_copy["start_time"],
                utc=True
            )

            events_copy["detected_at"] = pd.to_datetime(
                events_copy["detected_at"],
                utc=True
            )

        fig, axes = plt.subplots(
            4,
            2,
            figsize=(16, 18)
        )

        axes = axes.flatten()

        alert_count = (
            events_copy["event_type"]
            .eq("ALERT")
            .sum()
            if not events_copy.empty
            else 0
        )

        error_count = (
            events_copy["event_type"]
            .eq("ERROR")
            .sum()
            if not events_copy.empty
            else 0
        )

        system_status = (
            "ERROR"
            if error_count > 0
            else "ALERT"
            if alert_count > 0
            else "NORMAL"
        )

        fig.suptitle(
            "Predictive Maintenance Monitoring Dashboard",
            fontsize=18,
            y=0.98
        )

        fig.text(
            0.10,
            0.955,
            f"System Status: {system_status}",
            fontsize=12
        )

        fig.text(
            0.38,
            0.955,
            f"Alerts: {alert_count}",
            fontsize=12
        )

        fig.text(
            0.55,
            0.955,
            f"Errors: {error_count}",
            fontsize=12
        )

        fig.text(
            0.70,
            0.955,
            f"Processed Rows: {len(dashboard_df)}",
            fontsize=12
        )

        for index, axis in enumerate(
            self.axis_columns
        ):
            ax = axes[index]

            ax.plot(
                dashboard_df["sampled_at"],
                dashboard_df[axis],
                linewidth=1,
                label="Actual"
            )

            ax.plot(
                dashboard_df["sampled_at"],
                dashboard_df[
                    f"{axis}_predicted"
                ],
                linewidth=1.5,
                label="Predicted"
            )

            axis_events = events_copy[
                events_copy["axis"] == axis
            ]

            for _, event in axis_events.iterrows():
                ax.axvspan(
                    event["start_time"],
                    event["detected_at"],
                    alpha=0.25
                )

                ax.text(
                    event["detected_at"],
                    ax.get_ylim()[1] * 0.90,
                    (
                        f'{event["event_type"]}\n'
                        f'{event["duration_seconds"]:.0f}s'
                    ),
                    fontsize=8
                )

            min_c = thresholds[axis]["MinC"]
            max_c = thresholds[axis]["MaxC"]

            ax.set_title(
                f"{axis} | "
                f"MinC={min_c:.2f} | "
                f"MaxC={max_c:.2f}"
            )

            ax.set_xlabel("Time")
            ax.set_ylabel("Current")
            ax.grid(alpha=0.3)
            ax.legend(fontsize=8)

        plt.tight_layout(
            rect=[0, 0, 1, 0.94]
        )

        if save_path:
            plt.savefig(
                save_path,
                dpi=300,
                bbox_inches="tight"
            )

        plt.show()