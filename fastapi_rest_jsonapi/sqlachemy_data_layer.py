from fastapi_rest_jsonapi.data_layer import DataLayer
from sqlalchemy.orm.session import Session


class SQLAlchemyDataLayer(DataLayer):
    def __init__(self, session: Session, model):
        self.session: Session = session
        self.model = model

    def get(self) -> list:
        values = self.session.query(self.model).all()
        return values

    def get_one(self, id: int) -> object:
        value = self.session.query(self.model).get(id)
        return value

    def delete_one(self, id: int) -> bool:
        value = self.get_one(id)
        if value is None:
            return False
        self.session.delete(value)
        self.session.commit()
        return True
