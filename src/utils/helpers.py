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