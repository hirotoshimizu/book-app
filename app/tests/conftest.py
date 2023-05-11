import os
import time

import pytest
from dotenv import load_dotenv

from app import create_app
from app.dao.author import AuthorDAO
from app.dao.books import Book, BookDAO
from app.dao.genres import GenreDAO
from app.dao.publisher import PublisherDAO
from app.dao.tag import TagDAO
from app.neo4j import get_driver, init_driver


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            init_driver(
                os.environ.get("NEO4J_URI"),
                os.environ.get("NEO4J_USERNAME"),
                os.environ.get("NEO4J_PASSWORD"),
            )
        yield client


book = Book(
    book_id="test_book_123",
    title="test_book",
    sub_title="test_sub_title",
    summary="test_summary",
    publication_year=2023,
    edition=1,
    url="https://www.amazon.co.jp/",
    created_at=int(time.time()),
)

test = {
    "genre": "テストジャンル",
    "genre_en": "test_genre",
    "genre_uuid": "0fd45a74-d64d-4e6e-9631-b72d7821dbbe",
    "publisher": "test_publisher",
    "author": "John Doe",
    "tag": "test_tag",
}


@pytest.fixture
def register_test_data(app):
    with app.app_context():
        driver = get_driver()

        book_dao = BookDAO(driver)
        genre_dao = GenreDAO(driver)
        tag_dao = TagDAO(driver)
        author_dao = AuthorDAO(driver)
        publisher_dao = PublisherDAO(driver)

        genre_dao.register(test["genre"], test["genre_en"], test["genre_uuid"])
        book_dao.register(
            book, test["genre"], test["tag"], test["publisher"], test["author"]
        )
        yield
        book_dao.delete(book.book_id)
        author_dao.delete(test["author"])
        genre_dao.delete(test["genre_uuid"])
        tag_dao.delete(test["tag"])
        publisher_dao.delete(test["publisher"])
