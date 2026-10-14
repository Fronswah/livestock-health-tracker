# Livestock Health & Tracking System (LHTS)

A small, open-source Python program that helps livestock keepers record their animals and their health events, and see which animals are **due for a health check**. It was built for **PROG211 Object-Oriented Programming 1** (Limkokwing University of Creative Technology, Sierra Leone Campus) under **Digital Public Goods (DPG) standards**.

- **Domain:** Agriculture - Livestock Health & Tracking System
- **Author:** Francis Patrice Amara
- **Language:** Python 3.8 or newer (standard library only - nothing to install)
- **Licence:** MIT (free to use, copy, change and share)

## The problem

Small livestock keepers often keep animal records in notebooks or only in memory. When a disease appears, or an animal is sold, it is hard to see which animals were vaccinated or treated and when. LHTS gives a simple, offline way to keep this information in one place and to flag animals that have had no health event for six months.

## How the solution aligns with DPG standards

| DPG principle | How LHTS follows it |
|---|---|
| **Open source** | Published on GitHub under the MIT licence (`LICENSE`). All source code is plain `.py` files with comments and tests, so anyone can read, reuse and improve it. |
| **Inclusive and accessible design** | Works fully offline on any computer that has Python, including old and low-power machines. Uses a simple numbered text menu, short plain-English prompts and friendly error messages (no crashes or technical jargon). Needs no internet, no account and no paid software. |
| **Privacy-respecting (no sensitive personal data)** | Stores **no personal data**. Animals have anonymous tag IDs (for example `SL-CTL-001`) and a farm has only an anonymous code and a district. Tag and farm codes are limited to capital letters, digits and dashes, so names cannot be typed in by mistake. Free-text notes are automatically cleaned: phone-number-like text is replaced by `[removed]` (`Animal.clean_note`). |
| **Modular and reusable** | Code is split into a package: `models.py` (the `Animal` and `Farm` classes), `registry.py` (add/display functions that work with any objects), and `main.py` (the user interface). Classes can be reused in another program, for example a web app, without changing them. Unit tests in `tests/` protect each part. |

## Project structure

```
livestock-health-tracker/
|-- README.md
|-- LICENSE
|-- .gitignore
|-- main.py                  command-line program (menu and demo)
|-- livestock/
|   |-- __init__.py
|   |-- models.py            Animal and Farm classes
|   `-- registry.py          add_record / get_record / display_records (dictionary)
|-- tests/
|   |-- __init__.py
|   `-- test_livestock.py    16 unit tests
`-- docs/
    `-- screenshots/         screenshots of the program running
```

## How to run

1. Install Python 3.8 or newer from https://www.python.org
2. Download or clone this repository, then open a terminal in its folder.
3. Start the program:

```
python main.py            # interactive menu
python main.py --demo     # scripted demo that shows every feature
python -m unittest -v     # run the 16 unit tests
```

On some systems the command is `python3` instead of `python`.

## OOP concepts used (assignment tasks)

| Task | Where in the code |
|---|---|
| **Task 1 - Classes, attributes, methods, objects** | `Animal` (tag_id, species, breed, sex, birth_year, weight_kg, status, history) and `Farm` (farm_code, district, farm_type, registry). `main.py` creates objects and makes them interact: `Farm.record_health_event()` finds an `Animal` and calls its `record_event()`. |
| **Task 2 - One data structure** | `Farm.registry` is **one dictionary**: tag ID (key) to `Animal` object (value). `add_record()` and `display_records()` in `registry.py` add and display the records. |
| **Task 2 - Tuples (optional, extra marks)** | Fixed values are tuples (`Animal.SPECIES`, `Animal.HEALTH_EVENTS`, `SAMPLE_ANIMALS`, `MENU`). Each health event is a tuple `(date, event_type, note)` and an animal's history is a tuple of these events, which cannot be changed by accident. |
| **Task 3 - Instance methods** | `record_event()`, `update_weight()`, `set_status()`, `needs_check()`, `age_in_years()`, `display_info()`, `summary_line()` |
| **Task 3 - Class methods (`@classmethod`)** | `Animal.from_csv_line()` (alternative constructor), `Animal.total_registered()`, `Animal.reset_counter()` |
| **Static methods (`@staticmethod`)** | `Animal.is_valid_species()`, `Animal.clean_note()` |

## Example usage (sample input and output)

Typed input is shown after each prompt.

```
Farm code (e.g. FARM-BO-01): FARM-KB-02
District: Kambia
Farm type (cattle/goat/mixed...): goat

Choose a number: 1
Enter the animal's details (species: cattle, goat, sheep, pig, poultry)
Tag ID (e.g. SL-CTL-010): SL-GT-010
Species: goat
Breed: West African Dwarf
Sex (F/M): F
Birth year: 2024
Weight in kg: 21
Added: SL-GT-010 - goat (West African Dwarf)

Choose a number: 1
Tag ID (e.g. SL-CTL-010): SL-GT-011
...
Weight in kg: -3
Problem: Weight must be more than zero.

Choose a number: 4
Tag ID: SL-GT-010
Event type: vaccination
Note (no phone numbers or names): Routine round
Date YYYY-MM-DD (Enter = today): 2026-10-01
Recorded: vaccination on 2026-10-01

Choose a number: 3
Tag ID: SL-GT-010
Tag ID   : SL-GT-010
Animal   : Goat (West African Dwarf), female
Age      : 2 years (born 2024)
Weight   : 21.0 kg
Status   : active
Check due: No
Health history:
  2026-10-01  vaccination   Routine round
```

Output of `python main.py --demo` (sample data, fixed date 13 October 2026):

```
TAG ID       SPECIES  BREED               SEX  AGE     WEIGHT    STATUS
--------------------------------------------------------------------------
SL-CTL-001   cattle   Ndama               F    5 yr    260.0 kg  active
SL-CTL-005   cattle   Ndama               M    6 yr    310.0 kg  active
SL-GT-002    goat     West African Dwarf  F    3 yr    24.5 kg   active
SL-PIG-004   pig      Large White         F    2 yr    85.0 kg   active
SL-SHP-003   sheep    Djallonke           M    4 yr    35.0 kg   active
--------------------------------------------------------------------------
Total records: 5
```

## Limitations and future work

- Records are kept in memory only; they are lost when the program closes. A future version could save to a CSV or JSON file.
- The six-month health-check reminder is a simple rule, not veterinary advice. Always consult a qualified veterinary officer.
- Possible additions: Krio and other local-language prompts, a simple web or mobile interface, and an export for sharing herd data with agricultural officers.

## Licence

Released under the [MIT Licence](LICENSE).
