from marshmallow_jsonapi.fields import (
    Integer as MarshmallowInteger,
    String as MarshmallowString,
    Relationship as MarshmallowRelationship,
)


class Integer(MarshmallowInteger):
    ...


class String(MarshmallowString):
    ...


class Relationship(MarshmallowRelationship):
    ...
