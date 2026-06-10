from datetime import datetime, timedelta
from colorama import Fore, Style
from src.tracker.workout import Workout
from src.visualiser.charts import build_dataframe


def generate_weekly_summary(workouts: list[Workout]) -> None:
    """
    Print a formatted weekly performance summary to the terminal.
    Covers the last 7 days of training.
    """
    if not workouts:
        print(Fore.YELLOW + "No workout data to summarise yet.")
        return

    df = build_dataframe(workouts)

    if df.empty:
        return

    # Filter to last 7 days
    cutoff = datetime.now() - timedelta(days=7)
    # timedelta represents a duration — here, 7 days
    week_df = df[df["date"] >= cutoff]

    print(Fore.CYAN + "\n" + "═" * 50)
    print(Fore.CYAN + "       📅 WEEKLY PERFORMANCE SUMMARY")
    print(Fore.CYAN + "═" * 50)

    if week_df.empty:
        print(Fore.YELLOW + "  No workouts logged in the last 7 days.")
        print(Fore.CYAN + "═" * 50)
        return

    # --- Overall stats ---
    total_sessions = len(week_df)
    total_volume = week_df["total_volume"].sum()
    total_reps = week_df["total_reps"].sum()
    completion_rate = week_df["all_completed"].mean() * 100
    # .mean() on a boolean column gives the proportion of True values

    print(f"\n  {'Sessions this week:':<28} {Fore.GREEN}{total_sessions}")
    print(f"  {'Total reps performed:':<28} {Fore.GREEN}{int(total_reps):,}")
    print(f"  {'Total volume lifted:':<28} {Fore.GREEN}{total_volume:,.1f} kg")
    print(f"  {'Set completion rate:':<28} {Fore.GREEN}{completion_rate:.1f}%")
    # :<28 = left-align in a field of 28 characters (for neat columns)
    # :,.1f = format as float with 1 decimal and comma thousands separator

    # --- Per-exercise breakdown ---
    print(Fore.CYAN + "\n  📌 Exercise Breakdown:")
    print("  " + "─" * 46)

    exercises = week_df.groupby("exercise")

    for exercise_name, group in exercises:
        # group is a DataFrame containing only rows for this exercise
        sessions = len(group)
        avg_weight = group["avg_weight"].mean()
        max_weight = group["avg_weight"].max()
        vol = group["total_volume"].sum()

        print(f"\n  {Fore.YELLOW}{exercise_name}")
        print(f"    Sessions:      {sessions}")
        print(f"    Avg weight:    {avg_weight:.1f} kg")
        print(f"    Peak weight:   {max_weight:.1f} kg")
        print(f"    Total volume:  {vol:,.1f} kg")

    # --- Progress check (compare to previous week) ---
    prev_cutoff = cutoff - timedelta(days=7)
    prev_week_df = df[(df["date"] >= prev_cutoff) & (df["date"] < cutoff)]
    

    print(Fore.CYAN + "\n  📈 Week-on-Week Progress:")
    print("  " + "─" * 46)

    if prev_week_df.empty:
        print(f"  {Fore.YELLOW}  No previous week data to compare yet.")
    else:
        prev_volume = prev_week_df["total_volume"].sum()
        volume_change = total_volume - prev_volume
        pct_change = (volume_change / prev_volume * 100) if prev_volume > 0 else 0

        arrow = "↑" if volume_change >= 0 else "↓"
        colour = Fore.GREEN if volume_change >= 0 else Fore.RED

        print(f"\n  {'Previous week volume:':<28} {prev_volume:,.1f} kg")
        print(f"  {'This week volume:':<28} {total_volume:,.1f} kg")
        print(f"  {'Change:':<28} {colour}{arrow} {abs(volume_change):,.1f} kg ({abs(pct_change):.1f}%)")

    print(Fore.CYAN + "\n" + "═" * 50 + "\n")