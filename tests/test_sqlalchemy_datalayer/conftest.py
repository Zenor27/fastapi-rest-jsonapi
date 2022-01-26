from pytest import fixture
from fastapi import Path
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from fastapi_rest_jsonapi import RestAPI
from fastapi_rest_jsonapi.data import SQLAlchemyDataLayer
from fastapi_rest_jsonapi.schema import fields, Schema
from fastapi_rest_jsonapi.resource import ResourceDetail, ResourceList


@fixture()
def model_base():
    yield declarative_base()


@fixture()
def user_model(model_base):
    class User(model_base):
        __tablename__ = "user"

        id = Column(Integer, primary_key=True)
        name = Column(String)
        age = Column(Integer)

    yield User


@fixture()
def article_model(model_base, comment_model):
    class Article(model_base):
        __tablename__ = "article"

        id = Column(Integer, primary_key=True)
        name = Column(String)
        price = Column(Integer)
        comments = relationship("Comment", backref="article")

    yield Article


@fixture()
def comment_model(model_base):
    class Comment(model_base):
        __tablename__ = "comment"

        id = Column(Integer, primary_key=True)
        text = Column(String)
        author_id = Column(Integer, ForeignKey("author.id"))
        article_id = Column(Integer, ForeignKey("article.id"))

    yield Comment


@fixture()
def author_model(model_base, comment_model):
    class Author(model_base):
        __tablename__ = "author"

        id = Column(Integer, primary_key=True)
        name = Column(String)
        comments = relationship("Comment", backref="author")

    yield Author


@fixture()
def engine(user_model, author_model, comment_model, article_model) -> Engine:
    engine: Engine = create_engine(
        "sqlite:///:memory:",
        poolclass=QueuePool,
        connect_args={"check_same_thread": False},
    )
    user_model.metadata.create_all(engine)
    author_model.metadata.create_all(engine)
    comment_model.metadata.create_all(engine)
    article_model.metadata.create_all(engine)
    yield engine


@fixture()
def session(engine: Engine) -> Session:
    Session = sessionmaker(bind=engine)
    yield Session()


@fixture()
def user(session: Session, user_model):
    user = user_model(name="John", age=42)
    session.add(user)
    session.commit()
    yield user


@fixture()
def user_count():
    return 60


@fixture()
def users(session: Session, user_model, user_count):
    users = []
    for i in range(user_count, 0, -1):
        user = user_model(name=f"John {i}", age=i)
        users.append(user)
        session.add(user)
    session.commit()
    yield users


@fixture()
def user_schema():
    class UserSchema(Schema):
        __type__ = "user"

        id = fields.Integer()
        name = fields.String()
        age = fields.Integer()

    yield UserSchema


@fixture()
def user_list(user_schema, session: Session, user_model):
    class UserList(ResourceList):
        schema = user_schema
        data_layer = SQLAlchemyDataLayer(session, user_model)
        page_size = 0

    yield UserList


@fixture()
def author_schema():
    class AuthorSchema(Schema):
        __type__ = "author"

        id = fields.Integer()
        name = fields.String()

    yield AuthorSchema


@fixture()
def comment_schema(author_schema):
    class CommentSchema(Schema):
        __type__ = "comment"

        id = fields.Integer()
        text = fields.String()
        author_id = fields.Integer()
        author = fields.Relationship(schema="author", type_="author")

    yield CommentSchema


@fixture()
def article_schema(comment_schema):
    class ArticleSchema(Schema):
        __type__ = "article"

        id = fields.Integer()
        name = fields.String()
        price = fields.Integer()
        comments = fields.Relationship(schema="comment", many=True, type_="comment")

    yield ArticleSchema


@fixture()
def article_detail(article_schema, session: Session, article_model):
    class ArticleDetail(ResourceDetail):
        __view_parameters__ = {"id": (int, Path(..., title="id", ge=1))}
        schema = article_schema
        data_layer = SQLAlchemyDataLayer(session, article_model)

    yield ArticleDetail


@fixture()
def article_list(article_schema, session: Session, article_model):
    class ArticleList(ResourceList):
        schema = article_schema
        data_layer = SQLAlchemyDataLayer(session, article_model)
        page_size = 0

    yield ArticleList


@fixture()
def user_detail(user_schema, session: Session, user_model):
    class UserDetail(ResourceDetail):
        __view_parameters__ = {"id": (int, Path(..., title="id", ge=1))}
        schema = user_schema
        data_layer = SQLAlchemyDataLayer(session, user_model)

    yield UserDetail


@fixture(autouse=True)
def register_schema_routes(rest_api: RestAPI, user_list, user_detail, article_list, article_detail):
    rest_api.register(user_list, "/users")
    rest_api.register(user_detail, "/users/{id}")
    rest_api.register(article_list, "/articles")
    rest_api.register(article_detail, "/articles/{id}")


@fixture()
def generate_data():
    def _generate_data(user, only_fields=None):
        if only_fields is not None:
            attributes = {field: getattr(user, field) for field in only_fields}
        else:
            attributes = {
                "name": user.name,
                "age": user.age,
            }
        return {"type": "user", "id": user.id, "attributes": attributes}

    return _generate_data


@fixture()
def comment_count():
    return 20


@fixture()
def authors(session: Session, author_model, comment_count):
    authors = []
    for i in range(comment_count):
        author = author_model(name=f"Author {i}")
        authors.append(author)
        session.add(author)
    session.commit()
    yield authors


@fixture()
def comments(session: Session, authors, articles, comment_model, comment_count):
    comments = []
    for i in range(comment_count):
        comment = comment_model(text=f"comment {i}", author_id=authors[i].id, article_id=articles[i // 2].id)
        comments.append(comment)
        session.add(comment)
    session.commit()
    yield comments


@fixture()
def article_count():
    return 10


@fixture()
def articles(session: Session, article_model, article_count):
    articles = []
    for i in range(article_count):
        article = article_model(name=f"Article {i}", price=i)
        articles.append(article)
        session.add(article)
    session.commit()
    yield articles
