from sqlalchemy.orm.session import Session


class SQLAlchemyDataLayer:
    def __init__(self, session: Session, model):
        self.session: Session = session
        self.model = model

    def get(self) -> list:
        values = self.session.query(self.model).all()
        return values
