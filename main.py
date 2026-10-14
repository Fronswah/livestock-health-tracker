"""Livestock Health & Tracking System (LHTS) - command-line program.

Run:
    python main.py            interactive menu
    python main.py --demo     scripted demonstration with sample data
"""
import sys
from datetime import date

from livestock import Animal, Farm

DEMO_TODAY = date(2026, 10, 13)   # fixed date so the demo output is always the same

MENU = (
    "1. Add an animal",
    "2. Show all animals",
    "3. View one animal",
    "4. Record a health event",
    "5. Update an animal's weight",
    "6. Show animals due for a health check",
    "7. Show farm summary",
    "8. Load sample animals",
    "0. Exit",
)

SAMPLE_ANIMALS = (
    "SL-CTL-001,cattle,Ndama,F,2021,260",
    "SL-GT-002,goat,West African Dwarf,F,2023,24.5",
    "SL-SHP-003,sheep,Djallonke,M,2022,35",
    "SL-PIG-004,pig,Large White,F,2024,85",
    "SL-CTL-005,cattle,Ndama,M,2020,310",
)


def ask(question):
    """Ask the user a question and return the trimmed answer."""
    return input(question).strip()


def ask_date(question):
    """Ask for a date (YYYY-MM-DD). Pressing Enter means today."""
    answer = ask(question)
    return date.fromisoformat(answer) if answer else date.today()


def heading(text):
    print()
    print("=" * 74)
    print(text)
    print("=" * 74)


def add_animal_flow(farm):
    print("Enter the animal's details (species: " + ", ".join(Animal.SPECIES) + ")")
    animal = Animal(
        ask("Tag ID (e.g. SL-CTL-010): "), ask("Species: "), ask("Breed: "),
        ask("Sex (F/M): "), ask("Birth year: "), ask("Weight in kg: "))
    farm.add_animal(animal)
    print("Added: " + str(animal))


def view_animal_flow(farm):
    animal = farm.get_animal(ask("Tag ID: "))
    if animal is None:
        print("No animal found with that tag.")
    else:
        animal.display_info()


def record_event_flow(farm):
    print("Event types: " + ", ".join(Animal.HEALTH_EVENTS))
    event = farm.record_health_event(
        ask("Tag ID: "), ask("Event type: "), ask("Note (no phone numbers or names): "),
        ask_date("Date YYYY-MM-DD (Enter = today): "))
    print("Recorded: {} on {}".format(event[1], event[0].isoformat()))


def update_weight_flow(farm):
    animal = farm.get_animal(ask("Tag ID: "))
    if animal is None:
        print("No animal found with that tag.")
        return
    old, new = animal.update_weight(ask("New weight in kg: "))
    print("Weight changed from {:.1f} kg to {:.1f} kg.".format(old, new))


def due_flow(farm):
    due = farm.animals_due_for_check()
    if not due:
        print("Good news: no animals are due for a health check.")
    for animal in due:
        print("DUE: " + str(animal))


def load_sample_data(farm):
    for line in SAMPLE_ANIMALS:
        try:
            farm.add_animal(Animal.from_csv_line(line))
        except ValueError as problem:
            print("Skipped: " + str(problem))
    print("Sample animals loaded.")


def run_menu():
    heading("LIVESTOCK HEALTH & TRACKING SYSTEM")
    farm = Farm(ask("Farm code (e.g. FARM-BO-01): "), ask("District: "), ask("Farm type (cattle/goat/mixed...): "))
    actions = {
        "1": add_animal_flow, "2": lambda f: f.display_all(), "3": view_animal_flow,
        "4": record_event_flow, "5": update_weight_flow, "6": due_flow,
        "7": lambda f: f.display_summary(), "8": load_sample_data,
    }
    while True:
        print()
        print("\n".join(MENU))
        choice = ask("Choose a number: ")
        if choice == "0":
            print("Goodbye.")
            return
        action = actions.get(choice)
        if action is None:
            print("Please type a number from the menu.")
            continue
        try:
            action(farm)
        except ValueError as problem:     # friendly message instead of a crash
            print("Problem: " + str(problem))


def run_demo():
    """Scripted run that shows every required OOP feature."""
    today = DEMO_TODAY

    heading("STEP 1 - Create a Farm object")
    farm = Farm("FARM-BO-01", "Bo", "mixed")
    print("Created farm {} in {} district.".format(farm.farm_code, farm.district))

    heading("STEP 2 - Create Animal objects (constructor and class method)")
    first = Animal("SL-CTL-001", "cattle", "Ndama", "F", 2021, 260)
    farm.add_animal(first)
    print("Created with the constructor     : " + str(first))
    for line in SAMPLE_ANIMALS[1:]:
        animal = Animal.from_csv_line(line)
        farm.add_animal(animal)
        print("Created with Animal.from_csv_line: " + str(animal))
    print("Animal.total_registered() -> " + str(Animal.total_registered()))

    heading("STEP 3 - Data structure: dictionary registry (add and display)")
    try:
        farm.add_animal(Animal("SL-CTL-001", "cattle", "Ndama", "F", 2021, 260))
    except ValueError as problem:
        print("Duplicate blocked  -> " + str(problem))
    try:
        Animal("SL-XX-009", "dragon", "None", "F", 2022, 100)
    except ValueError as problem:
        print("Bad species blocked -> " + str(problem))
    farm.display_all(today)

    heading("STEP 4 - Objects interact: Farm asks Animal to record events")
    farm.record_health_event("SL-CTL-001", "vaccination", "Routine vaccination round", date(2026, 3, 2))
    farm.record_health_event("SL-CTL-001", "health check", "Vet visit, call 076123456 if needed", date(2026, 8, 20))
    farm.record_health_event("SL-GT-002", "deworming", "Whole flock dewormed", date(2026, 9, 10))
    farm.record_health_event("SL-SHP-003", "treatment", "Treated for foot rot", date(2025, 11, 15))
    farm.record_health_event("SL-CTL-005", "vaccination", "Routine vaccination round", date(2026, 1, 10))
    print("Events recorded. The phone number in the note was hidden for privacy:")
    farm.get_animal("SL-CTL-001").display_info(today)

    heading("STEP 5 - Instance methods: update weight and change status")
    old, new = farm.get_animal("SL-GT-002").update_weight(26.0)
    print("SL-GT-002 weight: {:.1f} kg -> {:.1f} kg".format(old, new))
    farm.get_animal("SL-PIG-004").set_status("sold")
    print("SL-PIG-004 status is now: " + farm.get_animal("SL-PIG-004").status)

    heading("STEP 6 - Animals due for a health check")
    for animal in farm.animals_due_for_check(today):
        last = animal.last_event_date()
        print("DUE: {}  (last event: {})".format(animal, last.isoformat() if last else "none"))

    heading("STEP 7 - Farm summary")
    farm.display_summary(today)
    print()
    print("Animals on the farm: {}   |   Animal objects created in this run: {}".format(
        len(farm.registry), Animal.total_registered()))
    print("(One extra object was created in Step 3 and then blocked as a duplicate.)")


def main():
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_menu()


if __name__ == "__main__":
    main()
