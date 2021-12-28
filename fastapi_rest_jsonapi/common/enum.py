import enum


class EnumMeta(enum.EnumMeta):
    def values(cls):
        return [e.value for e in cls]
