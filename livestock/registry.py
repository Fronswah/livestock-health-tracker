"""Registry functions: add and display records held in ONE dictionary.

The registry is a plain Python dictionary that maps each animal's tag ID (the
key) to its Animal object (the value). These functions do not depend on any
class, so they can be reused with any objects that have a ``tag_id`` and a
``summary_line()`` method.
"""


def add_record(registry, animal):
    """Add an animal to the registry. Raises ValueError if the tag already exists."""
    if animal.tag_id in registry:
        raise ValueError("Tag " + animal.tag_id + " is already registered.")
    registry[animal.tag_id] = animal
    return animal


def get_record(registry, tag_id):
    """Return the animal with this tag ID, or None if it is not found."""
    return registry.get(str(tag_id).strip().upper())


def display_records(registry, today=None):
    """Print one line for every animal in the registry, sorted by tag ID."""
    if not registry:
        print("No animals registered yet.")
        return
    print("{:<13}{:<9}{:<20}{:<5}{:<8}{:<10}{}".format(
        "TAG ID", "SPECIES", "BREED", "SEX", "AGE", "WEIGHT", "STATUS"))
    print("-" * 74)
    for tag_id in sorted(registry):
        print(registry[tag_id].summary_line(today))
    print("-" * 74)
    print("Total records: " + str(len(registry)))
