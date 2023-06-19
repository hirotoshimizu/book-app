import pytest

from app.dao.genres import GenreDAO
from app.exceptions.validation import ValidationException
from app.neo4j import get_driver
from app.tests.conftest import book, test_data


def test_all(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)
    result = dao.all()
    assert test_data["genre"]["name"] in str(result)


def test_register(app):
    with app.app_context():
        driver = get_driver()
        dao = GenreDAO(driver)
        dao.register(
            test_data["genre"]["name"],
            test_data["genre"]["name_en"],
            test_data["genre"]["uuid"],
        )
        result = dao.find(test_data["genre"]["uuid"])
        dao.delete(test_data["genre"]["uuid"])
        assert result["name"] == test_data["genre"]["name"]


def test_validation_error(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)

    with pytest.raises(ValidationException):
        dao.register(
            test_data["genre"]["name"],
            test_data["genre"]["name_en"],
            test_data["genre"]["uuid"],
        )


def test_update(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)
    output = dao.update("TEST-GENRE", "test_genre", test_data["genre"]["uuid"])
    assert output["name"] == "TEST-GENRE"
    assert output["name_en"] == "test_genre"
    assert output["uuid"] == test_data["genre"]["uuid"]


def test_delete(app):
    with app.app_context():
        driver = get_driver()
        dao = GenreDAO(driver)
        dao.register(
            test_data["genre"]["name"],
            test_data["genre"]["name_en"],
            test_data["genre"]["uuid"],
        )
        dao.delete(test_data["genre"]["uuid"])
        result = dao.find(test_data["genre"]["uuid"])
        assert result is None


def test_get_by_genre(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)
    records = dao.get_by_genre(test_data["genre"]["name_en"], 0, 1)
    for r in records:
        assert r["b"]["book_id"] == book.book_id
        for author in r["authors"]:
            assert author["name"] == test_data["author"]["name"]


def test_get_by_genre_total_count(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)
    output = dao.get_by_genre_total_count(test_data["genre"]["name_en"])
    assert output == 1


def test_find(register_test_data):
    driver = get_driver()
    dao = GenreDAO(driver)
    output = dao.find(test_data["genre"]["uuid"])
    assert output["name"] == test_data["genre"]["name"]
