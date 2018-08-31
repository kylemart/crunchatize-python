from tinydb import TinyDB, where


class DiskCache:
    """A simple database wrapper used for inserting, and checking for the
    existence of, a given value."""

    def __init__(self, filename):
        """Instantiates a new disk-based cache with the given filename."""
        self.db = TinyDB(filename)

    def put(self, value):
        """Puts a value into the cache."""
        self.db.insert({'value': value})

    def __contains__(self, value):
        """Returns True if the cache contains the value; False otherwise."""
        return self.db.search(where('value') == value)
