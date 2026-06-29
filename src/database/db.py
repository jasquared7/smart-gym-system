import sqlite3
import os

DB_PATH = "data/gym.db"


def get_connection() -> sqlite3.Connection:
    """
    Create and return a connection to the SQLite database.
    """
    os.makedirs("data", exist_ok=True)
    # don't crash if the folder already exists

    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)

    # row_factory makes query results behave like dictionaries
    conn.row_factory = sqlite3.Row

    # enable foreign key enforcement
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def initialise_database() -> None:
    """
    Create all tables if they don't already exist.
    """
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS workouts (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                date          TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS sets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                reps       INTEGER NOT NULL,
                weight_kg  REAL NOT NULL,
                completed  INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (workout_id) REFERENCES workouts(id)
            );
        """)
        # executescript() runs multiple SQL statements at once
        # CREATE TABLE IF NOT EXISTS = only create if it doesn't already exist
        # AUTOINCREMENT = database assigns IDs automatically
        # NOT NULL = must always have a value
        # UNIQUE = no two rows can have the same value in this column
        # REAL = SQLite's type for decimal numbers