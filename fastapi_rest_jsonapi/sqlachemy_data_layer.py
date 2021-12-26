from typing import List

from sqlalchemy.orm.query import Query
from fastapi_rest_jsonapi.data_layer import DataLayer
from sqlalchemy import desc
from sqlalchemy.orm.session import Session

from fastapi_rest_jsonapi.sort import Sort


class SQLAlchemyDataLayer(DataLayer):
    def __init__(self, session: Session, model):
        self.session: Session = session
        self.model = model

    def __sort_query(self, query: Query, sorts: list[Sort]) -> Query:
        for sort in sorts:
            if sort.ascending:
                query = query.order_by(getattr(self.model, sort.field))
            else:
                query = query.order_by(desc(getattr(self.model, sort.field)))
        return query

    def get(self, sorts: List[Sort]) -> list:
        query: Query = self.session.query(self.model)
        query = self.__sort_query(query, sorts)
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
