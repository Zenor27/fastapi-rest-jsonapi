from math import ceil

import sqlalchemy
from fastapi_rest_jsonapi.common.exceptions import (
    UnknownFieldException,
    UnknownRelationshipException,
    UnknownTypeException,
)
from fastapi_rest_jsonapi.data import DataLayer
from fastapi_rest_jsonapi.request.field import Field
from fastapi_rest_jsonapi.request.include import Include
from fastapi_rest_jsonapi.request.page import Page
from fastapi_rest_jsonapi.request.sort import Sort
from sqlalchemy import desc
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session


class SQLAlchemyDataLayer(DataLayer):
    def __init__(self, session: Session, model):
        self.session: Session = session
        self.model = model
        self.current_tablename = self.model.__tablename__

    def __get_model_for_type(self, type_: str):
        for registered_models in self.model.registry.mappers:
            class_ = registered_models.class_
            if class_.__tablename__ == type_:
                return class_
        raise UnknownTypeException(type_)

    def __get_relationships_and_properties_for_model(self, model) -> tuple[list[str], list[str]]:
        relationships = []
        properties = []
        for field_name, field_attr in model.__dict__.items():
            if type(getattr(field_attr, "property", False)) is sqlalchemy.orm.relationships.RelationshipProperty:
                relationships.append(field_name)
            elif type(getattr(field_attr, "property", False)):
                properties.append(field_name)

        return relationships, properties

    def __get_fields_for_type(self, type_: str, fields: list[Field]) -> tuple[list[str], list[str]]:
        type_model = self.__get_model_for_type(type_)
        type_relationship_fields, type_properties_fields = self.__get_relationships_and_properties_for_model(type_model)
        fields_ = list(filter(lambda f: f.type == type_, fields or []))
        fields_properties = filter(lambda f: f.field in type_properties_fields, fields_)
        fields_relationships = filter(lambda f: f.field in type_relationship_fields, fields_)
        fields_properties = map(lambda f: f.field, fields_properties)
        fields_relationships = map(lambda f: f.field, fields_relationships)
        return list(fields_properties), list(fields_relationships)

    def __get_include_field_type(self, include_field_type):
        current_type = self.current_tablename
        type_model = self.__get_model_for_type(current_type)
        model_field = getattr(type_model, include_field_type, None)
        if not model_field:
            raise UnknownFieldException(include_field_type)
        return model_field.mapper.class_.__tablename__

    def __sort_query(self, query: Query, sorts: list[Sort]) -> Query:
        for sort in sorts:
            if sort.ascending:
                query = query.order_by(getattr(self.model, sort.field))
            else:
                query = query.order_by(desc(getattr(self.model, sort.field)))
        return query

    def __paginate_query(self, query: Query, page: Page) -> Query:
        if page.size == 0:
            return query

        total = query.count()
        page.max_number = ceil(total / page.size)
        return query.offset(page.size * (page.number - 1)).limit(page.size)

    def __include_and_field_query(self, query: Query, includes: list[Include], fields: list[Field]) -> Query:
        processed_fields = []
        fields_properties, fields_relationship = self.__get_fields_for_type(self.current_tablename, fields)
        query = query.options(load_only(*fields_properties)) if fields_properties else query
        processed_fields.extend(fields_properties)
        processed_fields.extend(fields_relationship)

        for include in includes or []:
            joined_load_func = joinedload(include.field)
            include_field_type = self.__get_include_field_type(include.field)
            fields_, _ = self.__get_fields_for_type(include_field_type, fields)
            if fields_:
                processed_fields.extend(fields_)
                joined_load_func = joined_load_func.load_only(*fields_)
            query = query.options(joined_load_func)

        if processed_diff := set(processed_fields) ^ set([x.field for x in fields or []]):
            raise UnknownRelationshipException(", ".join(processed_diff))
        return query

    def get(
        self, sorts: list[Sort] = None, fields: list[Field] = None, page: Page = None, includes: list[Include] = None
    ) -> list:
        query: Query = self.session.query(self.model)
        query = self.__include_and_field_query(query, includes, fields)
        query = self.__sort_query(query, sorts)
        query = self.__paginate_query(query, page)
        return query.all()

    def get_one(self, id_: int, fields: list[Field] = None, includes: list[Include] = None) -> object:
        query: Query = self.session.query(self.model)
        query = self.__include_and_field_query(query, includes, fields)
        query = query.filter(self.model.id == id_)
        return query.one_or_none()

    def delete_one(self, id_: int) -> bool:
        obj = self.get_one(id_)
        if obj is None:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True

    def update_one(self, id_: int, **kwargs) -> object:
        obj = self.get_one(id_)
        if obj is None:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.commit()
        return obj

    def create_one(self, **kwargs) -> object:
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.commit()
        return obj
