from math import ceil
from sqlalchemy.orm.query import Query
from sqlalchemy import desc
from sqlalchemy.orm.session import Session
from fastapi_rest_jsonapi.data import DataLayer
from fastapi_rest_jsonapi.request.page import Page
from fastapi_rest_jsonapi.request.sort import Sort
from fastapi_rest_jsonapi.request.field import Field


class SQLAlchemyDataLayer(DataLayer):
    def __init__(self, session: Session, model):
        self.session: Session = session
        self.model = model

    def __table_name_to_model(self, table_name: str):
        for mapper in self.model.__mapper__.registry.mappers:
            class_ = mapper.class_
            if hasattr(class_, "__tablename__") and class_.__tablename__ == table_name:
                return class_

        raise ValueError(f"No model found for table {table_name}")

    def __sort_query(self, query: Query, sorts: list[Sort]) -> Query:
        for sort in sorts:
            if sort.ascending:
                query = query.order_by(getattr(self.model, sort.field))
            else:
                query = query.order_by(desc(getattr(self.model, sort.field)))
        return query

    def __field_query(self, fields: list[Field]) -> Query:
        if not fields:
            return self.session.query(self.model)

        query_fields = [self.model.id]
        for field in fields:
            field_model = self.__table_name_to_model(field.type)
            query_fields.append(getattr(field_model, field.field))

        return self.session.query(*query_fields)

    def __paginate_query(self, query: Query, page: Page) -> Query:
        if page.size == 0:
            return query

        total = query.count()
        page.max_number = ceil(total / page.size)
        return query.offset(page.size * (page.number - 1)).limit(page.size)

    def get(self, sorts: list[Sort], fields: list[Field], page: Page) -> list:
        query: Query = self.__field_query(fields)
        query = self.__sort_query(query, sorts)
        query = self.__paginate_query(query, page)
        return query.all()

    def get_one(self, id: int) -> object:
        obj = self.session.query(self.model).get(id)
        return obj

    def delete_one(self, id: int) -> bool:
        obj = self.get_one(id)
        if obj is None:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True

    def update_one(self, id: int, **kwargs) -> object:
        obj = self.get_one(id)
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
