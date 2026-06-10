import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from src.tracker.workout import Workout


# Where all chart images will be saved
REPORTS_DIR = "reports"


def build_dataframe(workouts: list[Workout]) -> pd.DataFrame:
    """
    Convert a list of Workout objects into a pandas DataFrame.

    Columns to create:
        date         | exercise     | avg_weight | total_volume | all_completed
        01/05/2026   | Bench Press  | 60.0       | 1440.0       | True
    """
    rows = []

    for workout in workouts:
        rows.append({
            "date": datetime.strptime(workout.date, "%d/%m/%Y %H:%M"),
            # strptime = "string parse time" — converts text into a datetime object
            # the format string must match exactly how date was saved in workout.py
            "exercise": workout.exercise_name,
            "avg_weight": workout.average_weight(),
            "total_volume": workout.total_volume(),
            "all_completed": workout.all_reps_completed(),
            "sets": len(workout.sets),
            "total_reps": sum(s.reps for s in workout.sets)
        })

    if not rows:
        return pd.DataFrame()  # return empty DataFrame if no data

    df = pd.DataFrame(rows)

    # Sort chronologically — important for line charts to make sense
    df = df.sort_values("date").reset_index(drop=True)
    # reset_index(drop=True) provides clean row numbers 0, 1, 2...
    # drop=True means don't keep the old index as a column

    return df


def plot_weight_progression(workouts: list[Workout], exercise_name: str) -> str:
    """
    Creates a line chart showing weight used over time for one exercise.
    Saves the chart as a PNG and returns the file path.

    Parameters:
        workouts: full workout history (will filter inside)
        exercise_name: e.g. "Bench Press"

    Returns:
        File path of the saved chart image.
    """
    df = build_dataframe(workouts)

    if df.empty:
        print("No data to visualise yet.")
        return ""

    # Filter to just the exercise we want
    # df[condition] filters rows where the condition is True
    exercise_df = df[df["exercise"].str.lower() == exercise_name.lower()]

    if exercise_df.empty:
        print(f"No data found for '{exercise_name}'.")
        return ""

    # --- Build the chart ---
    fig, ax = plt.subplots(figsize=(10, 5))
    # fig = the whole figure (canvas), ax = the axes (the plot area)
    # figsize=(width, height) in inches

    # Plot the weight line
    ax.plot(
        exercise_df["date"],
        exercise_df["avg_weight"],
        marker="o",          # show a dot at each data point
        linewidth=2,
        color="#4A90D9",
        label="Avg Weight (kg)"
    )

    # Colour the dots: green = completed all reps, red = failed
    for _, row in exercise_df.iterrows():
        # iterrows() loops over DataFrame rows as (index, row) pairs
        colour = "#2ECC71" if row["all_completed"] else "#E74C3C"
        ax.scatter(row["date"], row["avg_weight"], color=colour, s=100, zorder=5)
        # zorder=5 puts the dots on top of the line

    # Annotate each point with the weight value
    for _, row in exercise_df.iterrows():
        ax.annotate(
            f"{row['avg_weight']}kg",
            xy=(row["date"], row["avg_weight"]),
            xytext=(0, 10),              # offset 10 points above the dot
            textcoords="offset points",
            ha="center",
            fontsize=8,
            color="#333333"
        )

    # Format the x-axis to show dates nicely
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    plt.xticks(rotation=45)  # tilt labels so they don't overlap

    # Labels, title, legend
    ax.set_title(f"Weight Progression — {exercise_name}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Average Weight (kg)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    # alpha=0.5 makes the grid lines semi-transparent so they don't dominate

    # Add a legend for dot colours
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#2ECC71",
               markersize=10, label="All reps completed ✓"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#E74C3C",
               markersize=10, label="Incomplete reps ✗")
    ]
    ax.legend(handles=legend_elements, loc="upper left")

    plt.tight_layout()
    # tight_layout() automatically adjusts spacing so nothing gets cut off

    # Save the file
    safe_name = exercise_name.replace(" ", "_").lower()
    filepath = os.path.join(REPORTS_DIR, f"{safe_name}_progression.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    # plt.close() frees memory after saving the figure

    return filepath


def plot_volume_over_time(workouts: list[Workout]) -> str:
    """
    Bar chart showing total training volume per session across ALL exercises.
    Volume = weight × reps, so this shows how hard you worked each session.
    """
    df = build_dataframe(workouts)

    if df.empty:
        print("No data to visualise yet.")
        return ""

    # Group by date and sum the volume — one bar per session
    # .dt.date extracts just the date part (no time) for grouping
    df["day"] = df["date"].dt.date
    daily_volume = df.groupby("day")["total_volume"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.bar(
        range(len(daily_volume)),   # x positions: 0, 1, 2...
        daily_volume["total_volume"],
        color="#4A90D9",
        edgecolor="white",
        linewidth=0.8
    )

    # Colour bars by volume — darker = more volume
    max_vol = daily_volume["total_volume"].max()
    for bar, vol in zip(bars, daily_volume["total_volume"]):
        intensity = vol / max_vol  # 0.0 to 1.0
        bar.set_facecolor(plt.cm.Blues(0.3 + intensity * 0.7))
        # plt.cm.Blues is a colour map — 0=light, 1=dark blue

    # Add value labels on top of each bar
    for bar, vol in zip(bars, daily_volume["total_volume"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 50,
            f"{vol:,.0f}kg",
            ha="center", va="bottom", fontsize=8
        )

    # Set x-axis tick labels to dates
    ax.set_xticks(range(len(daily_volume)))
    ax.set_xticklabels(
        [str(d) for d in daily_volume["day"]],
        rotation=45, ha="right"
    )

    ax.set_title("Total Training Volume Per Session", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume (kg × reps)")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    # axis="y" means horizontal gridlines only — cleaner for bar charts

    plt.tight_layout()

    filepath = os.path.join(REPORTS_DIR, "volume_over_time.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()

    return filepath