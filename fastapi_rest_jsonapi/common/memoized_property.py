from functools import wraps


def memoized_property(property_func):
    attr_name = f"_{property_func.__name__}"

    @wraps(property_func)
    def memoized_property_func(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, property_func(self))
        return getattr(self, attr_name)

    return property(memoized_property_func)
