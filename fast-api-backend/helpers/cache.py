from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        """Return cached value or None."""
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        """Insert value into LRU cache."""
        if key in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
            return

        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)  # remove LRU entry

        self.cache[key] = value

    def clear(self):
        """Clear entire cache."""
        self.cache.clear()

    def remove(self, key):
        """Remove a single key if exists."""
        if key in self.cache:
            del self.cache[key]

    def __str__(self):
        return self.cache