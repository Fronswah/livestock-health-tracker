"""Unit tests for the LHTS classes. Run from the project folder with:
    python -m unittest -v
"""
import unittest
from datetime import date

from livestock import Animal, Farm, add_record


class AnimalTests(unittest.TestCase):
    def setUp(self):
        Animal.reset_counter()
        self.cow = Animal("SL-CTL-001", "cattle", "ndama", "f", 2021, 260)

    def test_attributes_are_cleaned(self):
        self.assertEqual(self.cow.tag_id, "SL-CTL-001")
        self.assertEqual(self.cow.breed, "Ndama")
        self.assertEqual(self.cow.sex, "F")
        self.assertEqual(self.cow.status, "active")

    def test_invalid_values_are_rejected(self):
        with self.assertRaises(ValueError):
            Animal("SL-X-1", "dragon", "x", "F", 2020, 100)
        with self.assertRaises(ValueError):
            Animal("SL-CTL-002", "cattle", "x", "Q", 2020, 100)
        with self.assertRaises(ValueError):
            Animal("SL-CTL-002", "cattle", "x", "F", 2020, -5)
        with self.assertRaises(ValueError):
            Animal("SL-CTL-002", "cattle", "x", "F", "abc", 100)
        with self.assertRaises(ValueError):
            Animal("bad tag!", "cattle", "x", "F", 2020, 100)

    def test_age(self):
        self.assertEqual(self.cow.age_in_years(date(2026, 10, 13)), 5)

    def test_record_event_and_privacy(self):
        event = self.cow.record_event("vaccination", "Call 076123456 now", date(2026, 3, 2))
        self.assertEqual(event, (date(2026, 3, 2), "vaccination", "Call [removed] now"))
        self.assertEqual(len(self.cow.history), 1)
        self.assertIsInstance(self.cow.history, tuple)

    def test_bad_event_type(self):
        with self.assertRaises(ValueError):
            self.cow.record_event("haircut")

    def test_needs_check(self):
        today = date(2026, 10, 13)
        self.assertTrue(self.cow.needs_check(today))             # no events yet
        self.cow.record_event("health check", "", date(2026, 9, 1))
        self.assertFalse(self.cow.needs_check(today))            # recent event
        self.assertTrue(self.cow.needs_check(date(2027, 6, 1)))  # more than 180 days later

    def test_update_weight(self):
        self.assertEqual(self.cow.update_weight(270), (260.0, 270.0))
        with self.assertRaises(ValueError):
            self.cow.update_weight(0)

    def test_inactive_animal_has_no_check_due(self):
        self.cow.set_status("sold")
        self.assertFalse(self.cow.needs_check(date(2026, 10, 13)))
        with self.assertRaises(ValueError):
            self.cow.record_event("treatment")

    def test_class_methods(self):
        goat = Animal.from_csv_line("SL-GT-002, goat, West African Dwarf, F, 2023, 24.5")
        self.assertEqual(goat.breed, "West African Dwarf")
        self.assertEqual(Animal.total_registered(), 2)
        with self.assertRaises(ValueError):
            Animal.from_csv_line("only,three,values")

    def test_static_methods(self):
        self.assertTrue(Animal.is_valid_species("goat"))
        self.assertFalse(Animal.is_valid_species("lion"))
        self.assertEqual(Animal.clean_note("Dose on 2026-03-02"), "Dose on 2026-03-02")


class FarmTests(unittest.TestCase):
    def setUp(self):
        Animal.reset_counter()
        self.farm = Farm("farm-bo-01", "bo", "mixed")
        self.farm.add_animal(Animal("SL-CTL-001", "cattle", "Ndama", "F", 2021, 260))
        self.farm.add_animal(Animal("SL-GT-002", "goat", "Dwarf", "F", 2023, 24))

    def test_farm_attributes(self):
        self.assertEqual(self.farm.farm_code, "FARM-BO-01")
        self.assertEqual(self.farm.district, "Bo")

    def test_registry_is_a_dictionary(self):
        self.assertIsInstance(self.farm.registry, dict)
        self.assertIn("SL-CTL-001", self.farm.registry)

    def test_duplicate_tag_rejected(self):
        with self.assertRaises(ValueError):
            add_record(self.farm.registry, Animal("SL-CTL-001", "cattle", "x", "M", 2020, 200))

    def test_get_animal_is_case_insensitive(self):
        self.assertIsNotNone(self.farm.get_animal(" sl-gt-002 "))
        self.assertIsNone(self.farm.get_animal("NOPE-1"))

    def test_objects_interact(self):
        self.farm.record_health_event("SL-CTL-001", "deworming", "", date(2026, 10, 1))
        self.assertEqual(len(self.farm.get_animal("SL-CTL-001").history), 1)
        with self.assertRaises(ValueError):
            self.farm.record_health_event("MISSING-1", "deworming")

    def test_animals_due_for_check(self):
        self.farm.record_health_event("SL-CTL-001", "deworming", "", date(2026, 10, 1))
        due = self.farm.animals_due_for_check(date(2026, 10, 13))
        self.assertEqual(tuple(a.tag_id for a in due), ("SL-GT-002",))


if __name__ == "__main__":
    unittest.main()
