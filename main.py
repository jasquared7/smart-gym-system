from colorama import Fore, Style, init
from src.tracker.user import User
from src.tracker.workout import Workout, Set
from src.tracker.progression import ProgressionEngine
from src.utils.helpers import save_workouts, load_workouts

# initialise colorama so we can use colored text in the terminal
init(autoreset=True)


def print_banner():
    #annoyingly could not get the banner to line up
    print(Fore.CYAN + """
╔══════════════════════════════════════╗
║      💪 SMART GYM SYSTEM v1.0       ║
║   Progressive Overload, Automated    ║
╚══════════════════════════════════════╝
    """ + Style.RESET_ALL)


def get_valid_float(prompt: str) -> float:
    """Keep asking until the user enters a valid number."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print(Fore.RED + "❌ Please enter a valid number (e.g. 60 or 62.5)")


def get_valid_int(prompt: str) -> int:
    """Keep asking until the user enters a valid whole number."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print(Fore.RED + "❌ Please enter a whole number (e.g. 3)")


def log_workout_flow(user: User, engine: ProgressionEngine) -> Workout:
    """
    Walk the user through logging a new workout session.
    Returns the completed Workout object.
    """
    print(Fore.YELLOW + "\n📋 LOG A WORKOUT")
    exercise_name = input("Exercise name (e.g. Bench Press): ").strip().title()
    # .strip() removes accidental spaces, .title() capitalises properly

    num_sets = get_valid_int("How many sets? ")

    # Get the recommendation BEFORE logging (so they can see what to aim for)
    last_workout = user.get_last_workout_for_exercise(exercise_name)
    recommendation = engine.recommend(exercise_name, last_workout)

    print(Fore.GREEN + f"\n🤖 AI Recommendation: {recommendation['message']}")

    if recommendation["weight_kg"]:
        print(Fore.GREEN + f"   → Target: {recommendation['sets']} sets x "
              f"{recommendation['reps']} reps @ {recommendation['weight_kg']}kg")

    print(Fore.YELLOW + "\nNow log what you actually did:\n")

    sets = []
    for i in range(num_sets):
        print(f"  Set {i + 1}:")
        weight = get_valid_float(f"    Weight (kg): ")
        reps = get_valid_int(f"    Reps completed: ")

        # Ask if they completed the target reps
        if recommendation["reps"] and reps < recommendation["reps"]:
            completed = False
            print(Fore.RED + f"    ⚠️  Below target ({recommendation['reps']} reps)")
        else:
            completed = True
            print(Fore.GREEN + f"    ✓ Target hit!")

        sets.append(Set(reps=reps, weight_kg=weight, completed=completed))

    workout = Workout(exercise_name=exercise_name, sets=sets)
    return workout


def view_history(user: User):
    """Display the user's full workout history."""
    if not user.workout_history:
        print(Fore.YELLOW + "\nNo workouts logged yet. Get lifting! 🏋️")
        return

    print(Fore.CYAN + f"\n📊 WORKOUT HISTORY FOR {user.name.upper()}")
    print("─" * 60)

    for workout in user.workout_history:
        print(workout)  # uses our __str__ method

    # Stats summary
    total_volume = sum(w.total_volume() for w in user.workout_history)
    print(Fore.GREEN + f"\n📈 Total volume lifted: {total_volume:,.1f} kg")


def main():
    print_banner()

    # --- User Setup ---
    name = input("Enter your name: ").strip().title()
    user = User(name)
    engine = ProgressionEngine()

    # Load saved workouts from file and add them to the user's history
    saved_workouts = load_workouts(name)
    for w in saved_workouts:
        user.workout_history.append(w)

    if saved_workouts:
        print(Fore.GREEN + f"✅ Loaded {len(saved_workouts)} previous workout(s) for {name}.")

    # --- Main Menu Loop ---
    while True:
        print(Fore.CYAN + "\n──────────── MENU ────────────")
        print("1. Log a workout")
        print("2. View workout history")
        print("3. Get recommendation for an exercise")
        print("4. Save & Exit")
        print("─────────────────────────────")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            workout = log_workout_flow(user, engine)
            user.add_workout(workout)
            save_workouts(user.name, user.workout_history)
            print(Fore.GREEN + f"\n✅ Logged: {workout}")

        elif choice == "2":
            view_history(user)

        elif choice == "3":
            exercise = input("Which exercise? ").strip().title()
            last = user.get_last_workout_for_exercise(exercise)
            rec = engine.recommend(exercise, last)
            print(Fore.GREEN + f"\n🤖 {rec['message']}")

        elif choice == "4":
            save_workouts(user.name, user.workout_history)
            print(Fore.CYAN + "\n💾 Progress saved. See you next session! 👋\n")
            break

        else:
            print(Fore.RED + "❌ Invalid option. Choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()