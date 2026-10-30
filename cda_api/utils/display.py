from dataclasses import fields


class PrettyPrint:
    """Base class that avoids displaying empty fields of objects (None, empty lists and dicts...)"""
    def __repr__(self) -> str:
        attributes = (
            f"{f.name}={getattr(self, f.name)!r}"
            for f in fields(self)
            if getattr(self, f.name)
        )
        return f"{type(self).__name__}({', '.join(attributes)})"
