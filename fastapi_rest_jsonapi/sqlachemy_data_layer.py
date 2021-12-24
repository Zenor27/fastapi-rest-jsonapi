from fastapi_rest_jsonapi.data_layer import DataLayer
from sqlalchemy.orm.session import Session


class SQLAlchemyDataLayer(DataLayer):
    def __init__(self, session: Session, model):
        self.session: Session = session
        self.model = model

    def get(self) -> list:
        objs = self.session.query(self.model).all()
        return objs

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
