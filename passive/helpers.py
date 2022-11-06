"""Helper functions."""

import inspect


def get_class_arguments(cls):
    """Get the arguments that the class should be initialized with."""
    attributes = inspect.getmembers(cls)
    fields = [a for a in attributes if a[0].startswith("__fields__")]
    return fields[0][-1].keys()
