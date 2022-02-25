import sys

class add_paths():
    def __init__(self, paths):
        self.paths = paths

    def __enter__(self):
        for path in self.paths:
            while path in sys.path:
                sys.path.remove(path)
            sys.path.insert(0, path)

    def __exit__(self, exc_type, exc_value, traceback):
        for path in self.paths:
            try:
                while path in sys.path:
                    sys.path.remove(path)
            except ValueError:
                pass