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
    image="test_book_123",
    created_at=int(time.time()),
)


test_data = {
    "author": {
        "uuid": "03d9942a-e560-4cb7-970c-7efbb7297815",
        "name": "John Doe",
    },
    "genre": {
        "uuid": "0fd45a74-d64d-4e6e-9631-b72d7821dbbe",
        "name": "テストジャンル",
        "name_en": "test_genre",
    },
    "publisher": {
        "uuid": "314fc552-51b7-46ce-99d8-d477d1a5ef7f",
        "name": "test_publisher",
    },
    "tag": {
        "uuid": "ac677768-a37f-444d-bac0-035a8aadb697",
        "name": "test_tag",
    },
}


@pytest.fixture
def register_test_data(app):
    with app.app_context():
        driver = get_driver()

        author_dao = AuthorDAO(driver)
        book_dao = BookDAO(driver)
        genre_dao = GenreDAO(driver)
        publisher_dao = PublisherDAO(driver)
        tag_dao = TagDAO(driver)

        author_dao.register(
            test_data["author"]["name"],
            test_data["author"]["uuid"],
        )
        genre_dao.register(
            test_data["genre"]["name"],
            test_data["genre"]["name_en"],
            test_data["genre"]["uuid"],
        )
        publisher_dao.register(
            test_data["publisher"]["name"],
            test_data["publisher"]["uuid"],
        )
        tag_dao.register(
            test_data["tag"]["name"],
            test_data["tag"]["uuid"],
        )
        book_dao.register(
            book,
            test_data["genre"]["name"],
            test_data["tag"]["name"],
            test_data["publisher"]["name"],
            test_data["author"]["name"],
        )
        yield
        book_dao.delete(book.book_id)
        author_dao.delete(test_data["author"]["uuid"])
        genre_dao.delete(test_data["genre"]["uuid"])
        tag_dao.delete(test_data["tag"]["uuid"])
        publisher_dao.delete(test_data["publisher"]["uuid"])
