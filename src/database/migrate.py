import json
import os
from src.database.db import initialise_database
from src.database.models import get_or_create_user, save_all_workouts
from src.tracker.workout import Workout

JSON_PATH = "data/workouts.json"
BACKUP_PATH = "data/workouts_backup.json"


def migrate():
    print("🔄 Starting migration from JSON → SQLite...\n")

    if not os.path.exists(JSON_PATH):
        print("ℹ️  No JSON file found. Nothing to migrate.")
        return

    # Read the JSON file
    with open(JSON_PATH, "r") as f:
        all_data = json.load(f)

    if not all_data:
        print("ℹ️  JSON file is empty. Nothing to migrate.")
        return

    # Set up the database tables
    initialise_database()

    migrated_users = 0
    migrated_workouts = 0

    for user_name, workout_list in all_data.items():
        print(f"  Migrating user: {user_name} ({len(workout_list)} workouts)...")

        # Get or create the user in the database
        user_id = get_or_create_user(user_name)

        # Rebuild Workout objects from the JSON data
        workouts = [Workout.from_dict(w) for w in workout_list]

        # Save to database
        save_all_workouts(user_id, workouts)

        migrated_users += 1
        migrated_workouts += len(workouts)

    # Rename JSON file as a backup
    os.rename(JSON_PATH, BACKUP_PATH)
    print(f"\n✅ Migration complete!")
    print(f"   Users migrated:    {migrated_users}")
    print(f"   Workouts migrated: {migrated_workouts}")
    print(f"   JSON backup saved to: {BACKUP_PATH}")
    print(f"\n   You can delete {BACKUP_PATH} once you've verified everything works.")


if __name__ == "__main__":
    migrate()