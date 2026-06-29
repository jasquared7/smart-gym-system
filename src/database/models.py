from src.database.db import get_connection
from src.tracker.workout import Workout, Set


# ─────────────────────────────────────────
#  USER OPERATIONS
# ─────────────────────────────────────────

def get_or_create_user(name: str) -> int:
    """
    Find a user by name and return their ID.
    If they don't exist yet, create them first.

    Returns the user's integer ID from the database.
    """
    with get_connection() as conn:
        # Try to find existing user
        row = conn.execute(
            "SELECT id FROM users WHERE name = ?", (name,)
        ).fetchone()

        if row:
            return row["id"]

        # User not found — create them
        cursor = conn.execute(
            "INSERT INTO users (name) VALUES (?)", (name,)
        )
        conn.commit()
        # saves the change permanently

        return cursor.lastrowid
        # lastrowid = the auto-generated ID of the row just inserted


# ─────────────────────────────────────────
#  SAVING WORKOUTS
# ─────────────────────────────────────────

def save_workout(user_id: int, workout: Workout) -> None:
    """
    Save a single workout to the database.
    """
    with get_connection() as conn:
        # Insert the workout record
        cursor = conn.execute(
            """
            INSERT INTO workouts (user_id, exercise_name, date)
            VALUES (?, ?, ?)
            """,
            (user_id, workout.exercise_name, workout.date)
        )
        workout_id = cursor.lastrowid

        # Insert each set linked to this workout
        for s in workout.sets:
            conn.execute(
                """
                INSERT INTO sets (workout_id, reps, weight_kg, completed)
                VALUES (?, ?, ?, ?)
                """,
                (workout_id, s.reps, s.weight_kg, int(s.completed))
            )

        conn.commit()


def save_all_workouts(user_id: int, workouts: list[Workout]) -> None:
    """
    Save multiple workouts at once.
    Clears existing workouts for this user first to avoid duplicates.
    """
    with get_connection() as conn:
        # Find all workout IDs for this user
        rows = conn.execute(
            "SELECT id FROM workouts WHERE user_id = ?", (user_id,)
        ).fetchall()

        workout_ids = [row["id"] for row in rows]

        # Delete all sets belonging to those workouts
        if workout_ids:
            placeholders = ",".join("?" * len(workout_ids))
            # Builds "?,?,?" dynamically based on how many IDs we have
            conn.execute(
                f"DELETE FROM sets WHERE workout_id IN ({placeholders})",
                workout_ids
            )

        # Delete the workouts themselves
        conn.execute(
            "DELETE FROM workouts WHERE user_id = ?", (user_id,)
        )

        conn.commit()

    # Now save all workouts afresh
    for workout in workouts:
        save_workout(user_id, workout)


# ─────────────────────────────────────────
#  LOADING WORKOUTS
# ─────────────────────────────────────────

def load_workouts(user_id: int) -> list[Workout]:
    """
    Load all workouts for a user, with their sets, from the database.
    """
    with get_connection() as conn:
        # First get all workouts for this user
        workout_rows = conn.execute(
            """
            SELECT id, exercise_name, date
            FROM workouts
            WHERE user_id = ?
            ORDER BY date ASC
            """,
            (user_id,)
        ).fetchall()

        workouts = []

        for w_row in workout_rows:
            # For each workout, fetch its sets
            set_rows = conn.execute(
                """
                SELECT reps, weight_kg, completed
                FROM sets
                WHERE workout_id = ?
                ORDER BY id ASC
                """,
                (w_row["id"],)
            ).fetchall()

            # Rebuild Set objects
            sets = [
                Set(
                    reps=row["reps"],
                    weight_kg=row["weight_kg"],
                    completed=bool(row["completed"])
                    # bool() converts 1/0 back to True/False
                )
                for row in set_rows
            ]

            # Rebuild the Workout object
            workout = Workout(exercise_name=w_row["exercise_name"], sets=sets)
            workout.date = w_row["date"]
            workouts.append(workout)

    return workouts