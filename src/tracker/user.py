class User:
    """
    Represents a gym user with a name and their workout history.
    
    """

    def __init__(self, name: str):
        self.name = name
        self.workout_history = []  # list to store all past workouts

    def add_workout(self, workout):
        self.workout_history.append(workout) # add a new workout to the user's history

    def get_last_workout_for_exercise(self, exercise_name: str):
        """
        Looks through history to find the most recent
        time the user did a specific exercise.
        Returns None if they've never done it.
        """
        # reversed() lets us loop backwards without modifying the list
        for workout in reversed(self.workout_history):
            if workout.exercise_name.lower() == exercise_name.lower():
                return workout
        return None

    def __str__(self):
        """
        This method ensures that when we print the user object,
        it appears in a clean and easy to read format showing their
        name and how many workouts they've logged.
        """
        return f"User: {self.name} | Workouts logged: {len(self.workout_history)}"