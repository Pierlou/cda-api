class NullObject:
    def __getattr__(self, name):
        return None

    def __repr__(self):
        return "NullObject"
