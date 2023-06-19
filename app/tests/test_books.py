import time

import pytest

from app.dao.author import AuthorDAO
from app.dao.books import Book, BookDAO
from app.dao.genres import GenreDAO
from app.dao.publisher import PublisherDAO
from app.dao.tag import TagDAO
from app.exceptions.validation import ValidationException
from app.neo4j import get_driver
from app.tests.conftest import book, test_data

book2 = Book(
    book_id="test_book_123_2",
    title="test_book_2",
    sub_title="test_sub_title",
    summary="test_summary",
    publication_year=2023,
    edition=1,
    url="https://www.amazon.co.jp/",
    image="test_book_123_2",
    created_at=int(time.time()),
)

# test_data2 = {
#     "genre": "テストジャンル2",
#     "genre_en": "test_genre_2",
#     "genre_uuid": "3146dad5-cafb-4a21-a64b-80eabbd44152",
#     "publisher": "test_publisher_2",
#     "author": "John Doe 2",
#     "tag": "test_tag",
# }

test_data2 = {
    "author": {"name": "John Doe 2", "uuid": "77426c18-0801-4530-a1ec-ebdb58355fde"},
    "genre": {
        "name": "テストジャンル2",
        "name_en": "test_genre_2",
        "uuid": "3146dad5-cafb-4a21-a64b-80eabbd44152",
    },
    "publisher": {
        "name": "test_publisher_2",
        "uuid": "4b0ce5d1-9754-4f1c-8ba7-385b28b3f9b8",
    },
    "tag": {"name": "test_tag", "uuid": "79bcc7a9-af0c-4769-b1a9-b6c7b6f33c31"},
}


def test_all(register_test_data):
    driver = get_driver()
    dao = BookDAO(driver)

    result = dao.all(0, 1)

    assert result[0]["b"]["title"] == book.title


def test_register(app):
    with app.app_context():
        driver = get_driver()

        author_dao = AuthorDAO(driver)
        book_dao = BookDAO(driver)
        genre_dao = GenreDAO(driver)
        tag_dao = TagDAO(driver)
        publisher_dao = PublisherDAO(driver)

        author_dao.register(
            test_data["author"]["name"],
            test_data["author"]["uuid"],
        )
        genre_dao.register(
            test_data["genre"]["name"],
            test_data["genre"]["name_en"],
            test_data["genre"]["uuid"],
        )
        tag_dao.register(
            test_data["tag"]["name"],
            test_data["tag"]["uuid"],
        )
        publisher_dao.register(
            test_data["publisher"]["name"],
            test_data["publisher"]["uuid"],
        )
        book_dao.register(
            book,
            test_data["genre"]["name"],
            test_data["tag"]["name"],
            test_data["publisher"]["name"],
            test_data["author"]["name"],
        )

        result = book_dao.search("test")

        author_dao.delete(test_data["author"]["uuid"])
        book_dao.delete(book.book_id)
        genre_dao.delete(test_data["genre"]["uuid"])
        tag_dao.delete(test_data["tag"]["uuid"])
        publisher_dao.delete(test_data["publisher"]["uuid"])

        assert result[0]["b"]["title"] == book.title


def test_validation_error(register_test_data):
    driver = get_driver()
    dao = BookDAO(driver)

    with pytest.raises(ValidationException):
        dao.register(
            book,
            test_data["genre"]["name"],
            test_data["tag"]["name"],
            test_data["publisher"]["name"],
            test_data["author"]["name"],
        )


def test_delete(app):
    with app.app_context():
        driver = get_driver()

        author_dao = AuthorDAO(driver)
        book_dao = BookDAO(driver)
        genre_dao = GenreDAO(driver)
        tag_dao = TagDAO(driver)
        publisher_dao = PublisherDAO(driver)

        author_dao.register(
            test_data["author"]["name"],
            test_data["author"]["uuid"],
        )
        genre_dao.register(
            test_data["genre"]["name"],
            test_data["genre"]["name_en"],
            test_data["genre"]["uuid"],
        )
        tag_dao.register(
            test_data["tag"]["name"],
            test_data["tag"]["uuid"],
        )
        publisher_dao.register(
            test_data["publisher"]["name"],
            test_data["publisher"]["uuid"],
        )
        book_dao.register(
            book,
            test_data["genre"]["name"],
            test_data["tag"]["name"],
            test_data["publisher"]["name"],
            test_data["author"]["name"],
        )
        search_result = book_dao.search(book.book_id)

        author_dao.delete(test_data["author"]["uuid"])
        book_dao.delete(book.book_id)
        genre_dao.delete(test_data["genre"]["uuid"])
        tag_dao.delete(test_data["tag"]["uuid"])
        publisher_dao.delete(test_data["publisher"]["uuid"])
        delete_result = book_dao.search(book.book_id)

        assert search_result[0]["b"]["title"] == book.title
        assert delete_result == []


def test_get_total_count(app):
    with app.app_context():
        driver = get_driver()

        author_dao = AuthorDAO(driver)
        book_dao = BookDAO(driver)
        genre_dao = GenreDAO(driver)
        tag_dao = TagDAO(driver)
        publisher_dao = PublisherDAO(driver)

        before_test_add = book_dao.get_total_count()

        author_dao.register(
            test_data["author"]["name"],
            test_data["author"]["uuid"],
        )
        genre_dao.register(
            test_data["genre"]["name"],
            test_data["genre"]["name_en"],
            test_data["genre"]["uuid"],
        )
        tag_dao.register(
            test_data["tag"]["name"],
            test_data["tag"]["uuid"],
        )
        publisher_dao.register(
            test_data["publisher"]["name"],
            test_data["publisher"]["uuid"],
        )
        book_dao.register(
            book,
            test_data["genre"]["name"],
            test_data["tag"]["name"],
            test_data["publisher"]["name"],
            test_data["author"]["name"],
        )

        after_test_add = book_dao.get_total_count()

        author_dao.delete(test_data["author"]["uuid"])
        book_dao.delete(book.book_id)
        genre_dao.delete(test_data["genre"]["uuid"])
        tag_dao.delete(test_data["tag"]["uuid"])
        publisher_dao.delete(test_data["publisher"]["uuid"])
        assert 1 == after_test_add - before_test_add


def test_latest(register_test_data):
    driver = get_driver()
    dao = BookDAO(driver)
    result = dao.latest(1)
    assert result[0]["b"]["title"] == book.title


def test_detail(register_test_data):
    driver = get_driver()
    dao = BookDAO(driver)
    result = dao.detail(book.book_id)
    assert result["b"]["sub_title"] == book.sub_title
    assert result["b"]["publication_year"] == book.publication_year


def test_relate(register_test_data):
    driver = get_driver()

    author_dao = AuthorDAO(driver)
    book_dao = BookDAO(driver)
    genre_dao = GenreDAO(driver)
    publisher_dao = PublisherDAO(driver)
    tag_dao = TagDAO(driver)

    author_dao.register(
        test_data2["author"]["name"],
        test_data2["author"]["uuid"],
    )
    genre_dao.register(
        test_data2["genre"]["name"],
        test_data2["genre"]["name_en"],
        test_data2["genre"]["uuid"],
    )
    publisher_dao.register(
        test_data2["publisher"]["name"],
        test_data2["publisher"]["uuid"],
    )
    tag_dao.register(
        test_data2["tag"]["name"],
        test_data2["tag"]["uuid"],
    )
    book_dao.register(
        book2,
        test_data2["genre"]["name"],
        test_data2["tag"]["name"],
        test_data2["publisher"]["name"],
        test_data2["author"]["name"],
    )

    result = book_dao.relate(book2.book_id)

    book_dao.delete(book2.book_id)
    author_dao.delete(test_data2["author"]["uuid"])
    genre_dao.delete(test_data2["genre"]["uuid"])
    tag_dao.delete(test_data2["tag"]["uuid"])
    publisher_dao.delete(test_data2["publisher"]["uuid"])

    assert book.title == result[0]["related_book"]["title"]


def test_search(register_test_data):
    driver = get_driver()
    dao = BookDAO(driver)

    result = dao.search(book.book_id)

    assert book.book_id == result[0]["b"]["book_id"]
    assert book.title == result[0]["b"]["title"]
    assert book.sub_title == result[0]["b"]["sub_title"]
    assert test_data["author"]["name"] == result[0]["authors"][0]["name"]


def test_get_search_count(register_test_data):
    driver = get_driver()
    dao = BookDAO(driver)

    count_by_book_id = dao.get_search_count(book.book_id)
    count_by_title = dao.get_search_count(book.title)
    count_by_sub_title = dao.get_search_count(book.sub_title)
    count_by_author = dao.get_search_count(test_data["author"]["name"])

    assert count_by_book_id == 1
    assert count_by_title == 1
    assert count_by_sub_title == 1
    assert count_by_author == 1


def test_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
