import pytest

from app.dao.genres import GenreDAO
from app.dao.publisher import PublisherDAO
from app.neo4j import get_driver
from app.tests.conftest import book, test


def test_all(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)

    result = dao.all()

    assert test["genre"] in str(result)


def test_register(app):
    with app.app_context():
        driver = get_driver()
        dao = GenreDAO(driver)
        publisher_dao = PublisherDAO(driver)

        dao.register(test["genre"], test["genre_en"], test["genre_uuid"])
        result = dao.find(test["genre_uuid"])
        dao.delete(test["genre_uuid"])
        publisher_dao.delete(test["publisher"])

        assert result["name"] == test["genre"]


def test_update(app):
    with app.app_context():
        driver = get_driver()

        dao = GenreDAO(driver)


def test_update(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)

    output = dao.update("TEST-GENRE", "test_genre", test["genre_uuid"])

    assert output["name"] == "TEST-GENRE"
    assert output["name_en"] == "test_genre"
    assert output["uuid"] == test["genre_uuid"]


def test_delete(app):
    with app.app_context():
        driver = get_driver()

        dao = GenreDAO(driver)
        publisher_dao = PublisherDAO(driver)

        dao.register(test["genre"], test["genre_en"], test["genre_uuid"])
        dao.delete(test["genre_uuid"])
        publisher_dao.delete(test["publisher"])
        result = dao.find(test["genre_en"])

        assert result is None


def test_get_by_genre(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)

    records = dao.get_by_genre(test["genre_en"], 0, 1)

    for r in records:
        assert r["b"]["book_id"] == book.book_id
        for author in r["authors"]:
            assert author["name"] == test["author"]


def test_get_by_genre_total_count(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)

    output = dao.get_by_genre_total_count(test["genre_en"])

    assert output == 1


def test_find(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)

    output = dao.find(test["genre_uuid"])
    print(output)

    assert output["name"] == test["genre"]
