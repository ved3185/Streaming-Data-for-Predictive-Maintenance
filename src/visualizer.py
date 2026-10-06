from pathlib import Path
import pandas as pd

import matplotlib.pyplot as plt


class AnalysisVisualizer:
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

    def plot_regressions(self, dataframe, save_path=None):
        fig, axes = plt.subplots(
            4,
            2,
            figsize=(14, 16)
        )

        axes = axes.flatten()

        for index, axis in enumerate(self.axis_columns):
            ax = axes[index]

            ax.hexbin(
                dataframe["elapsed_seconds"],
                dataframe[axis],
                gridsize=45,
                mincnt=1,
                cmap="Blues",
                linewidths=0,
                label="Actual density"
            )

            ax.plot(
                dataframe["elapsed_seconds"],
                dataframe[f"{axis}_predicted"],
                color="darkorange",
                linewidth=2,
                label="Linear fit"
            )

            ax.set_title(axis)
            ax.set_xlabel("Elapsed Time (seconds)")
            ax.set_ylabel("Current")
            ax.legend()
            ax.grid(alpha=0.3)

        fig.suptitle(
            "Current Density and Linear Fit by Axis",
            fontsize=16
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(
                save_path,
                dpi=300,
                bbox_inches="tight"
            )

        plt.show()

    def plot_residuals(self, dataframe, save_path=None):
        fig, axes = plt.subplots(
            4,
            2,
            figsize=(14, 16)
        )

        axes = axes.flatten()

        for index, axis in enumerate(self.axis_columns):
            ax = axes[index]
            residuals = dataframe[f"{axis}_residual"].dropna()
            positive_residuals = residuals[residuals > 0]

            ax.hist(
                residuals,
                bins=40,
                color="slateblue",
                alpha=0.78,
                edgecolor="white"
            )

            ax.axvline(
                x=0,
                linestyle="--",
                linewidth=1,
                color="black",
                label="Zero residual"
            )

            if not positive_residuals.empty:
                ax.axvline(
                    positive_residuals.quantile(0.95),
                    color="darkorange",
                    linestyle=":",
                    linewidth=1.5,
                    label="95th percentile"
                )
                ax.axvline(
                    positive_residuals.quantile(0.99),
                    color="crimson",
                    linestyle="-.",
                    linewidth=1.5,
                    label="99th percentile"
                )

            ax.set_title(f"{axis} Residual Distribution")
            ax.set_xlabel("Residual current")
            ax.set_ylabel("Record count")
            ax.grid(alpha=0.3)
            ax.legend(fontsize=8)

        fig.suptitle(
            "Residual Distributions and Upper-Tail Cutoffs",
            fontsize=16
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(
                save_path,
                dpi=300,
                bbox_inches="tight"
            )

        plt.show()

    def plot_event_overlays(
    self,
    dataframe,
    events_df,
    save_path=None
    ):
        fig, axes = plt.subplots(
            4,
            2,
            figsize=(14, 16)
        )

        axes = axes.flatten()

        plot_df = dataframe.copy()

        plot_df["sampled_at"] = pd.to_datetime(
            plot_df["sampled_at"],
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

        for index, axis in enumerate(self.axis_columns):
            ax = axes[index]

            ax.plot(
                plot_df["sampled_at"],
                plot_df[axis],
                linewidth=1,
                label="Actual"
            )

            ax.plot(
                plot_df["sampled_at"],
                plot_df[f"{axis}_predicted"],
                linewidth=2,
                label="Regression"
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

                label_text = (
                    f'{event["event_type"]}\n'
                    f'{event["duration_seconds"]:.0f}s'
                )

                event_rows = plot_df[
                    (
                        plot_df["sampled_at"]
                        >= event["start_time"]
                    )
                    &
                    (
                        plot_df["sampled_at"]
                        <= event["detected_at"]
                    )
                ]

                if not event_rows.empty:
                    annotation_y = (
                        event_rows[axis].max()
                    )

                    ax.annotate(
                        label_text,
                        xy=(
                            event["detected_at"],
                            annotation_y
                        ),
                        xytext=(5, 10),
                        textcoords="offset points",
                        fontsize=9
                    )

            ax.set_title(axis)
            ax.set_xlabel("Time")
            ax.set_ylabel("Current")
            ax.grid(alpha=0.3)
            ax.legend()

        fig.suptitle(
            "Regression Monitoring with Alert and Error Events",
            fontsize=16
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(
                save_path,
                dpi=300,
                bbox_inches="tight"
            )

        plt.show()