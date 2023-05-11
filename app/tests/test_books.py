import time

import pytest

from app.dao.author import AuthorDAO
from app.dao.books import Book, BookDAO
from app.dao.genres import GenreDAO
from app.dao.publisher import PublisherDAO
from app.dao.tag import TagDAO
from app.neo4j import get_driver
from app.tests.conftest import book, test

another_book = Book(
    book_id="test_book_123_2",
    title="test_book_2",
    sub_title="test_sub_title",
    summary="test_summary",
    publication_year=2023,
    edition=1,
    url="https://www.amazon.co.jp/",
    created_at=int(time.time()),
)

another_test = {
    "genre": "テストジャンル2",
    "genre_en": "test_genre_2",
    "genre_uuid": "3146dad5-cafb-4a21-a64b-80eabbd44152",
    "publisher": "test_publisher_2",
    "author": "John Doe 2",
    "tag": "test_tag",
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

        genre_dao.register(test["genre"], test["genre_en"], test["genre_uuid"])
        book_dao.register(
            book, test["genre"], test["tag"], test["publisher"], test["author"]
        )

        result = book_dao.search("test")

        author_dao.delete(test["author"])
        book_dao.delete(book.book_id)
        genre_dao.delete(test["genre_uuid"])
        tag_dao.delete(test["tag"])
        publisher_dao.delete(test["publisher"])

        assert result[0]["b"]["title"] == book.title


def test_delete(app):
    with app.app_context():
        driver = get_driver()

        author_dao = AuthorDAO(driver)
        book_dao = BookDAO(driver)
        genre_dao = GenreDAO(driver)
        tag_dao = TagDAO(driver)
        publisher_dao = PublisherDAO(driver)

        genre_dao.register(test["genre"], test["genre_en"], test["genre_uuid"])
        book_dao.register(
            book, test["genre"], test["tag"], test["publisher"], test["author"]
        )
        search_result = book_dao.search(book.book_id)

        author_dao.delete(test["author"])
        book_dao.delete(book.book_id)
        genre_dao.delete(test["genre_uuid"])
        tag_dao.delete(test["tag"])
        publisher_dao.delete(test["publisher"])
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

        genre_dao.register(test["genre"], test["genre_en"], test["genre_uuid"])
        book_dao.register(
            book, test["genre"], test["tag"], test["publisher"], test["author"]
        )

        after_test_add = book_dao.get_total_count()

        author_dao.delete(test["author"])
        book_dao.delete(book.book_id)
        genre_dao.delete(test["genre_uuid"])
        tag_dao.delete(test["tag"])
        publisher_dao.delete(test["publisher"])

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
    book_dao = BookDAO(driver)
    genre_dao = GenreDAO(driver)
    tag_dao = TagDAO(driver)
    author_dao = AuthorDAO(driver)
    publisher_dao = PublisherDAO(driver)

    genre_dao.register(
        another_test["genre"], another_test["genre_en"], another_test["genre_uuid"]
    )
    book_dao.register(
        another_book,
        another_test["genre"],
        another_test["tag"],
        another_test["publisher"],
        another_test["author"],
    )

    result = book_dao.relate(another_book.book_id)

    book_dao.delete(another_book.book_id)
    author_dao.delete(another_test["author"])
    genre_dao.delete(another_test["genre_uuid"])
    tag_dao.delete(another_test["tag"])
    publisher_dao.delete(another_test["publisher"])

    assert book.title == result[0]["related_book"]["title"]


def test_search(register_test_data):
    driver = get_driver()
    dao = BookDAO(driver)

    result = dao.search(book.book_id)

    assert book.book_id == result[0]["b"]["book_id"]
    assert book.title == result[0]["b"]["title"]
    assert book.sub_title == result[0]["b"]["sub_title"]
    assert test["author"] == result[0]["authors"][0]["name"]


def test_get_search_count(register_test_data):
    driver = get_driver()
    dao = BookDAO(driver)

    count_by_book_id = dao.get_search_count(book.book_id)
    count_by_title = dao.get_search_count(book.title)
    count_by_sub_title = dao.get_search_count(book.sub_title)
    count_by_author = dao.get_search_count(test["author"])

    assert count_by_book_id == 1
    assert count_by_title == 1
    assert count_by_sub_title == 1
    assert count_by_author == 1


def test_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
