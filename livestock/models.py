"""Core classes for the Livestock Health & Tracking System (LHTS).

Privacy by design: an animal is identified only by an anonymous tag and a farm
only by an anonymous farm code. The system never stores names, phone numbers
or addresses of people, and free-text notes are cleaned of phone numbers.
"""
import re
from datetime import date

from .registry import add_record, get_record, display_records

# Matches phone-number-like text: 8 or more digits, optionally split by single spaces or dashes.
_PHONE_PATTERN = re.compile(r"\+?\d(?:[\s-]?\d){7,}")
_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


def _hide_phone(match):
    """Replace a phone-like match with [removed], but keep ISO dates (2026-03-02)."""
    text = match.group(0)
    return text if _DATE_PATTERN.fullmatch(text) else "[removed]"


# Anonymous codes may only contain capital letters, digits and dashes.
_CODE_PATTERN = re.compile(r"^[A-Z0-9-]{3,20}$")


def _to_number(value, kind, label):
    """Convert text to int/float, raising a friendly ValueError if it fails."""
    try:
        return kind(value)
    except (TypeError, ValueError):
        raise ValueError(label + " must be a number.")


class Animal:
    """One animal in a herd.

    Attributes (instance): tag_id, species, breed, sex, birth_year, weight_kg,
    status and a read-only health history stored as a tuple of event tuples.
    """

    # Fixed lists of allowed values are tuples because they must never change.
    SPECIES = ("cattle", "goat", "sheep", "pig", "poultry")
    SEXES = ("F", "M")
    HEALTH_EVENTS = ("vaccination", "deworming", "treatment", "health check")
    STATUSES = ("active", "sold", "deceased")
    CHECK_INTERVAL_DAYS = 180   # a health event is expected at least every 6 months
    MAX_NOTE_LENGTH = 120

    _total_registered = 0       # class attribute shared by every Animal object

    def __init__(self, tag_id, species, breed, sex, birth_year, weight_kg):
        tag_id = str(tag_id).strip().upper()
        species = str(species).strip().lower()
        sex = str(sex).strip().upper()

        if not _CODE_PATTERN.match(tag_id):
            raise ValueError("Tag ID must be 3-20 characters: capital letters, digits or dashes.")
        if not Animal.is_valid_species(species):
            raise ValueError("Species must be one of: " + ", ".join(Animal.SPECIES) + ".")
        if sex not in Animal.SEXES:
            raise ValueError("Sex must be F (female) or M (male).")
        birth_year = _to_number(birth_year, int, "Birth year")
        if not 1990 <= birth_year <= date.today().year:
            raise ValueError("Birth year must be between 1990 and this year.")
        weight_kg = _to_number(weight_kg, float, "Weight")
        if weight_kg <= 0:
            raise ValueError("Weight must be more than zero.")

        self.tag_id = tag_id
        self.species = species
        self.breed = str(breed).strip().title() or "Unknown"
        self.sex = sex
        self.birth_year = birth_year
        self.weight_kg = weight_kg
        self.status = "active"
        self._history = ()      # tuple of (date, event_type, note) tuples
        Animal._total_registered += 1

    # ------------------------------------------------------------------
    # Instance methods (work on one particular animal)
    # ------------------------------------------------------------------
    @property
    def history(self):
        """The health history as an immutable tuple of (date, event, note)."""
        return self._history

    def age_in_years(self, today=None):
        """Approximate age in whole years, based on the birth year."""
        today = today or date.today()
        return today.year - self.birth_year

    def record_event(self, event_type, note="", on_date=None):
        """Add a health event (vaccination, deworming, treatment, health check)."""
        event_type = str(event_type).strip().lower()
        if event_type not in Animal.HEALTH_EVENTS:
            raise ValueError("Event must be one of: " + ", ".join(Animal.HEALTH_EVENTS) + ".")
        if self.status != "active":
            raise ValueError("Cannot record events for an animal that is " + self.status + ".")
        event = (on_date or date.today(), event_type, Animal.clean_note(note))
        self._history = self._history + (event,)    # tuples are immutable, so build a new one
        return event

    def update_weight(self, new_weight_kg):
        """Replace the animal's weight with a new measurement."""
        new_weight_kg = _to_number(new_weight_kg, float, "Weight")
        if new_weight_kg <= 0:
            raise ValueError("Weight must be more than zero.")
        old = self.weight_kg
        self.weight_kg = new_weight_kg
        return old, new_weight_kg

    def set_status(self, status):
        """Change status to active, sold or deceased."""
        status = str(status).strip().lower()
        if status not in Animal.STATUSES:
            raise ValueError("Status must be one of: " + ", ".join(Animal.STATUSES) + ".")
        self.status = status

    def last_event_date(self):
        """Date of the most recent health event, or None if there is none."""
        return max((event[0] for event in self._history), default=None)

    def needs_check(self, today=None):
        """True if this active animal has had no health event for too long."""
        if self.status != "active":
            return False
        last = self.last_event_date()
        if last is None:
            return True
        today = today or date.today()
        return (today - last).days > Animal.CHECK_INTERVAL_DAYS

    def summary_line(self, today=None):
        """One formatted line used in the records table."""
        return "{:<13}{:<9}{:<20}{:<5}{:<8}{:<10}{}".format(
            self.tag_id, self.species, self.breed, self.sex,
            str(self.age_in_years(today)) + " yr",
            "{:.1f} kg".format(self.weight_kg), self.status)

    def display_info(self, today=None):
        """Print a full information card, including the health history."""
        today = today or date.today()
        sex_word = "female" if self.sex == "F" else "male"
        print("Tag ID   : " + self.tag_id)
        print("Animal   : {} ({}), {}".format(self.species.title(), self.breed, sex_word))
        print("Age      : {} years (born {})".format(self.age_in_years(today), self.birth_year))
        print("Weight   : {:.1f} kg".format(self.weight_kg))
        print("Status   : " + self.status)
        print("Check due: " + ("YES - no recent health event" if self.needs_check(today) else "No"))
        print("Health history:")
        if not self._history:
            print("  (no events recorded)")
        for event_date, event_type, note in self._history:
            print("  {}  {:<13} {}".format(event_date.isoformat(), event_type, note))

    def __str__(self):
        return self.tag_id + " - " + self.species + " (" + self.breed + ")"

    # ------------------------------------------------------------------
    # Class methods (work on the class as a whole)
    # ------------------------------------------------------------------
    @classmethod
    def from_csv_line(cls, line):
        """Alternative constructor: build an Animal from 'tag,species,breed,sex,year,kg'."""
        parts = tuple(part.strip() for part in str(line).split(","))
        if len(parts) != 6:
            raise ValueError("Expected 6 values: tag,species,breed,sex,birth_year,weight_kg.")
        return cls(*parts)

    @classmethod
    def total_registered(cls):
        """How many Animal objects have been created so far."""
        return cls._total_registered

    @classmethod
    def reset_counter(cls):
        """Set the shared counter back to zero (used by the tests)."""
        cls._total_registered = 0

    # ------------------------------------------------------------------
    # Static methods (utility functions that need no object or class)
    # ------------------------------------------------------------------
    @staticmethod
    def is_valid_species(species):
        """True if the species is one the system supports."""
        return species in Animal.SPECIES

    @staticmethod
    def clean_note(text):
        """Privacy helper: hide phone-number-like text and limit the note length."""
        text = _PHONE_PATTERN.sub(_hide_phone, str(text).strip())
        return text[:Animal.MAX_NOTE_LENGTH]


class Farm:
    """A farm that owns a registry (one dictionary) of Animal objects.

    The farm is identified by an anonymous code and a district only. It talks to
    its Animal objects to record events and to find animals that need attention.
    """

    def __init__(self, farm_code, district, farm_type="mixed"):
        farm_code = str(farm_code).strip().upper()
        if not _CODE_PATTERN.match(farm_code):
            raise ValueError("Farm code must be 3-20 characters: capital letters, digits or dashes.")
        self.farm_code = farm_code
        self.district = str(district).strip().title()
        self.farm_type = str(farm_type).strip().lower()
        self.registry = {}      # the ONE data structure: dict of tag_id -> Animal

    def add_animal(self, animal):
        """Register an animal on this farm."""
        return add_record(self.registry, animal)

    def get_animal(self, tag_id):
        """Find an animal by tag ID (None if not found)."""
        return get_record(self.registry, tag_id)

    def record_health_event(self, tag_id, event_type, note="", on_date=None):
        """Find the animal, then ask it to record the event (object interaction)."""
        animal = self.get_animal(tag_id)
        if animal is None:
            raise ValueError("No animal found with tag " + str(tag_id).strip().upper() + ".")
        return animal.record_event(event_type, note, on_date)

    def animals_due_for_check(self, today=None):
        """Tuple of animals that need a health check, in tag order."""
        return tuple(self.registry[tag] for tag in sorted(self.registry)
                     if self.registry[tag].needs_check(today))

    def display_all(self, today=None):
        """Print the table of all animals on the farm."""
        display_records(self.registry, today)

    def display_summary(self, today=None):
        """Print a short report about the whole herd."""
        active = tuple(a for a in self.registry.values() if a.status == "active")
        print("Farm code : {}   District: {}   Type: {}".format(
            self.farm_code, self.district, self.farm_type))
        print("Animals   : {} registered, {} active".format(len(self.registry), len(active)))
        for species in Animal.SPECIES:
            count = sum(1 for a in active if a.species == species)
            if count:
                print("  {:<8}: {}".format(species.title(), count))
        print("Due for a health check: " + str(len(self.animals_due_for_check(today))))
