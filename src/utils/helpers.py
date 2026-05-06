import json
import os
from src.tracker.workout import Workout


DATA_FILE = "data/workouts.json"


def save_workouts(user_name: str, workouts: list[Workout]) -> None:
    """
    Save all of a user's workouts to a JSON file.
    
    A universal format for storing structured data as text.
    """
    # Load existing data first so we don't overwrite other users
    all_data = _load_raw_data()

    # Store this user's workouts under their name as the key
    all_data[user_name] = [w.to_dict() for w in workouts]

    # 'with' statement automatically closes the file when done
    with open(DATA_FILE, "w") as f:
        # indent=2 makes the JSON human-readable
        json.dump(all_data, f, indent=2)

    print(f"✅ Workout saved for {user_name}.")


def load_workouts(user_name: str) -> list[Workout]:
    """
    Load all saved workouts for a specific user from the JSON file.
    Returns an empty list if no data exists yet.
    """
    all_data = _load_raw_data()

    if user_name not in all_data:
        return []  # first-time user, no history yet

    # Rebuild Workout objects from the raw dictionaries using our from_dict() method
    return [Workout.from_dict(w) for w in all_data[user_name]]


def _load_raw_data() -> dict:
    """
    Internal helper: load the entire JSON file as a Python dict.
    If the file doesn't exist yet, return an empty dict.
    """
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)