from typing import Optional, Any
from marshmallow import class_registry
from marshmallow_jsonapi import Schema as MarshmallowSchema
from marshmallow_jsonapi.fields import Relationship as MarshmallowRelationship
from fastapi_rest_jsonapi.common.exceptions import UnknownFieldException, UnknownSchemaException
from fastapi_rest_jsonapi.request.field import Field
from fastapi_rest_jsonapi.request.include import Include
from fastapi_rest_jsonapi.schema.fields import Relationship


class Schema(MarshmallowSchema):
    def __init_subclass__(cls, *_, **__):
        cls.Meta.type_ = cls.__type__
        return super().__init_subclass__()

    def __get_schema_class_from_field(self, field: str) -> type["Schema"]:
        if field not in self.declared_fields:
            raise UnknownFieldException(field)
        field_schema_type: str = self.declared_fields[field].__dict__["_Relationship__schema"]
        field_schema_cls: list[type[Schema]] = next(
            filter(
                lambda schema_class: getattr(schema_class[0], "__type__", None) == field_schema_type,
                class_registry._registry.values(),
            ),
            None,
        )
        if field_schema_cls is None:
            raise UnknownSchemaException(field_schema_type)

        return field_schema_cls[0]

    def _dump(self, obj, many):
        return super().dump(obj, many=many)

    def __get_relationship_fields(self, fields: list[Field]) -> list[Field]:
        relationship_fields = []
        for field in fields:
            field_ = field.field
            if declared_field := self.declared_fields.get(field_):
                if type(declared_field) is MarshmallowRelationship or type(declared_field) is Relationship:
                    relationship_fields.append(field)
        return relationship_fields

    def __handle_includes_and_relationships(
        self,
        obj_dump: dict,
        root_obj: dict,
        obj: Any,
        relationship_fields: list[Field],
        includes: list[Include],
        only: list[str],
        fields: list[Field],
    ):
        should_append_relationships = includes and not only
        if relationship_fields or should_append_relationships:
            obj_dump["relationships"] = {}

        for field in relationship_fields:
            field_ = field.field
            include_schema_cls = self.__get_schema_class_from_field(field_)
            field_relationship = include_schema_cls().dump(
                [],
                [Field(include_schema_cls.__type__, "id")],
                getattr(obj, field_),
                many=self.declared_fields[field_].many,
            )
            obj_dump["relationships"][field_] = field_relationship

        for include in includes:
            field = include.field
            include_schema_cls = self.__get_schema_class_from_field(field)
            many = self.declared_fields[field].many
            obj_field = getattr(obj, field)
            field_included = include_schema_cls().dump(
                [],
                [
                    Field(include_schema_cls.__type__, x.field)
                    for x in fields or []
                    if x.type == include_schema_cls.__type__
                ],
                obj_field,
                many=many,
            )
            root_obj["included"].extend(field_included["data"])

            if should_append_relationships and field not in obj_dump["relationships"]:
                field_relationship = include_schema_cls().dump(
                    [],
                    [Field(include_schema_cls.__type__, "id")],
                    obj_field,
                    many=many,
                )
                obj_dump["relationships"][field] = field_relationship

    def dump(self, includes: list[Include], fields: list[Field], obj: Any, many: Optional[bool] = None):
        current_type_fields = [x for x in fields or [] if x.type == self.__type__]
        relationship_fields = self.__get_relationship_fields(current_type_fields)
        only = [x.field for x in current_type_fields] + ["id"] if current_type_fields else None
        obj_dump = self.__class__(only=only)._dump(obj, many=many)
        if includes:
            obj_dump["included"] = []

        if many:
            for idx in range(len(obj)):
                self.__handle_includes_and_relationships(
                    obj_dump["data"][idx], obj_dump, obj[idx], relationship_fields, includes, only, fields
                )
        else:
            self.__handle_includes_and_relationships(
                obj_dump["data"], obj_dump, obj, relationship_fields, includes, only, fields
            )

        return obj_dump
