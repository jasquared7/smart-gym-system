class ProgressionEngine:
    """
    The brain of the system.
    
    Progressive overload principle: to get stronger, you must
    gradually increase the stress on your muscles over time.
    This engine automates that decision-making.
    """

    # Class-level constants — values that never change
    # Using variable constants instead of numbers makes code easier to understand
    WEIGHT_INCREASE_PERCENT = 0.05   # increase weight by 5%
    WEIGHT_DECREASE_PERCENT = 0.10   # decrease weight by 10% on failure
    DELOAD_THRESHOLD = 3             # failed sets in a row = plateau

    def __init__(self):
        # Track consecutive failures per exercise: {"Bench Press": 2, ...}
        self.consecutive_failures: dict[str, int] = {}

    def recommend(self, exercise_name: str, last_workout) -> dict:
        """
        Given the user's last workout for an exercise,
        return a recommendation for their next session.

        Parameters:
            exercise_name: e.g. "Bench Press"
            last_workout: a Workout object, or None if it is the first time doing this exercise.

        Returns:
            A dictionary with recommended weight, reps, and a message.
        """

        # --- Case 1: First time doing this exercise ---
        if last_workout is None:
            return {
                "weight_kg": None,
                "reps": None,
                "sets": None,
                "message": (
                    f"First time logging {exercise_name}! "
                    "Start with a weight you can comfortably lift for 8 reps. "
                    "Focus on form over weight."
                ),
                "status": "first_time"
            }

        last_weight = last_workout.average_weight()
        last_reps = last_workout.sets[0].reps if last_workout.sets else 8
        num_sets = len(last_workout.sets)

        # --- Case 2: All reps completed — increase weight ---
        if last_workout.all_reps_completed():
            # Reset failure counter since they succeeded
            self.consecutive_failures[exercise_name] = 0

            new_weight = round(last_weight * (1 + self.WEIGHT_INCREASE_PERCENT), 1)

            # Round to nearest 2.5kg (standard gym plate increment)
            new_weight = self._round_to_nearest(new_weight, 2.5)

            return {
                "weight_kg": new_weight,
                "reps": last_reps,
                "sets": num_sets,
                "message": (
                    f"Great work last session! You completed all reps. "
                    f"Increase to {new_weight}kg this session. 💪"
                ),
                "status": "increase"
            }

        # --- Case 3: Failed to complete all reps — check for plateau ---
        else:
            failures = self.consecutive_failures.get(exercise_name, 0) + 1
            self.consecutive_failures[exercise_name] = failures

            # Plateau detected — deload (drop weight significantly for recovery)
            if failures >= self.DELOAD_THRESHOLD:
                deload_weight = round(last_weight * 0.90, 1)
                deload_weight = self._round_to_nearest(deload_weight, 2.5)
                self.consecutive_failures[exercise_name] = 0  # reset after deload

                return {
                    "weight_kg": deload_weight,
                    "reps": last_reps,
                    "sets": num_sets,
                    "message": (
                        f"You've hit a plateau on {exercise_name} after {failures} sessions. "
                        f"Deloading to {deload_weight}kg. This is normal — recovery leads to growth. 🔄"
                    ),
                    "status": "deload"
                }

            # Regular failure — keep the weight, encourage completion
            return {
                "weight_kg": last_weight,
                "reps": last_reps,
                "sets": num_sets,
                "message": (
                    f"You didn't complete all reps last time. Stay at {last_weight}kg "
                    f"and focus on hitting all {last_reps} reps before increasing. "
                    f"({failures}/{self.DELOAD_THRESHOLD} failures before deload)"
                ),
                "status": "maintain"
            }

    def _round_to_nearest(self, value: float, nearest: float) -> float:
        """
        Round a number to the nearest increment.
        e.g. _round_to_nearest(62.3, 2.5) → 62.5
        
        The underscore prefix (_) is a Python convention meaning
        'this is a private method — only use it inside this class'.
        """
        return round(round(value / nearest) * nearest, 1)