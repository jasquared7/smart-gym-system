from datetime import datetime

def _normalise_date(date_str: str) -> str:
    """
    Accepts dates in either old format (YYYY-MM-DD HH:MM)
    or new format (DD/MM/YYYY HH:MM) and always returns
    the new format. To handle existing saved data.
    """
    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%d/%m/%Y %H:%M")
        except ValueError:
            continue
    return date_str  # fallback: return as-is if neither format matches

class Set:
    """
    Represents a single set within an exercise.
    e.g. "3 sets of 8 reps at 60kg".
    """

    def __init__(self, reps: int, weight_kg: float, completed: bool = True):
        self.reps = reps
        self.weight_kg = weight_kg
        self.completed = completed  # did the user complete intended reps? (True/False)

    def to_dict(self) -> dict:
        """
        Converts this Set into a plain Python dictionary.
        This is needed to save data to a JSON file later.
        """
        return {
            "reps": self.reps,
            "weight_kg": self.weight_kg,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        The reverse of to_dict() — rebuilds a Set from a dictionary.
        
        @classmethod means this method belongs to the class, not an instance.
        'cls' refers to the Set class itself.
        Used as an alternative constructor: Set.from_dict(some_dict)
        """
        return cls(
            reps=data["reps"],
            weight_kg=data["weight_kg"],
            completed=data["completed"]
        )


class Workout:
    """
    Represents one exercise session.
    e.g. "Bench Press — 3 sets on 14/02/2025"
    """

    def __init__(self, exercise_name: str, sets: list[Set]):
        self.exercise_name = exercise_name
        self.sets = sets
        # datetime.now() captures the exact moment this workout was created
        self.date = datetime.now().strftime("%d/%m/%Y %H:%M")

    def all_reps_completed(self) -> bool:
        """Returns True if the user completed every rep in every set."""
        return all(s.completed for s in self.sets)
        # 'all()' returns True only if every item in the iterable is True

    def average_weight(self) -> float:
        """Calculate the average weight lifted across all sets."""
        if not self.sets:
            return 0.0
        total = sum(s.weight_kg for s in self.sets)
        return total / len(self.sets)

    def total_volume(self) -> float:
        """
        Volume = weight x reps, summed across all sets.
        """
        return sum(s.weight_kg * s.reps for s in self.sets)

    def to_dict(self) -> dict:
        """Serialise this Workout to a dict so we can save it as JSON."""
        return {
            "exercise_name": self.exercise_name,
            "date": self.date,
            "sets": [s.to_dict() for s in self.sets]
            # loops over self.sets, calls to_dict() on each
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Rebuild a Workout object from a saved dictionary."""
        sets = [Set.from_dict(s) for s in data["sets"]]
        workout = cls(exercise_name=data["exercise_name"], sets=sets)
        workout.date = _normalise_date(data["date"])  # restore the original date, not the current time 
        return workout

    def __str__(self):
        sets_info = " | ".join(
            f"Set {i+1}: {s.reps} reps @ {s.weight_kg}kg {'✓' if s.completed else '✗'}"
            for i, s in enumerate(self.sets)
        )
        return f"[{self.date}] {self.exercise_name} — {sets_info}"