import csv
from datetime import datetime
from src.database.db import initialise_database
from src.database.models import get_or_create_user, save_workout, load_workouts as db_load
from src.tracker.workout import Workout


def save_workouts(user_name: str, workouts: list[Workout]) -> None:
    """
    Save all workouts for a user.
    """
    user_id = get_or_create_user(user_name)

    from src.database.models import save_all_workouts
    save_all_workouts(user_id, workouts)

    print(f"✅ Workouts saved for {user_name}.")


def load_workouts(user_name: str) -> list[Workout]:
    """
    Load all workouts for a user from the database.
    Returns an empty list if no data exists yet.
    """
    initialise_database()
    user_id = get_or_create_user(user_name)
    return db_load(user_id)


def export_to_csv(user_name: str, workouts: list) -> str:
    """
    Export a user's full workout history to a CSV file.
    Returns the file path of the exported CSV.
    """
    if not workouts:
        print("No workouts to export.")
        return ""

    # Build the file path with a timestamp so exports don't overwrite each other
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
    filename = f"data/{user_name.lower()}_workouts_{timestamp}.csv"

    # Define the column headers
    fieldnames = [
        "date", "exercise", "set_number",
        "weight_kg", "reps", "completed", "set_volume"
    ]

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # writes the column names as the first row

        for workout in workouts:
            for i, s in enumerate(workout.sets, start=1):
                writer.writerow({
                    "date": workout.date,
                    "exercise": workout.exercise_name,
                    "set_number": i,
                    "weight_kg": s.weight_kg,
                    "reps": s.reps,
                    "completed": "Yes" if s.completed else "No",
                    "set_volume": round(s.weight_kg * s.reps, 1)
                })

    print(f"✅ Exported to {filename}")
    return filename