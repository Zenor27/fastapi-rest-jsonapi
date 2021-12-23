from marshmallow_jsonapi import Schema as MarshmallowSchema


class Schema(MarshmallowSchema):
    def __init_subclass__(cls, *_, **__):
        cls.Meta.type_ = cls.__type__
        return super().__init_subclass__()
