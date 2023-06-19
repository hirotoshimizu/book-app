import pytest

from app.dao.author import AuthorDAO
from app.exceptions.validation import ValidationException
from app.neo4j import get_driver
from app.tests.conftest import test_data


def test_all(register_test_data):
    driver = get_driver()
    dao = AuthorDAO(driver)
    result = dao.all()
    assert test_data["author"]["name"] in str(result)


def test_register(app):
    with app.app_context():
        driver = get_driver()
        dao = AuthorDAO(driver)

        dao.register(test_data["author"]["name"], test_data["author"]["uuid"])
        result = dao.find(test_data["author"]["uuid"])
        dao.delete(test_data["author"]["uuid"])

        assert result["name"] == test_data["author"]["name"]


def test_validation_error(register_test_data):
    driver = get_driver()
    dao = AuthorDAO(driver)

    with pytest.raises(ValidationException):
        dao.register(test_data["author"]["name"], test_data["author"]["uuid"])


def test_update(register_test_data):
    driver = get_driver()
    dao = AuthorDAO(driver)
    output = dao.update("Tanaka Taro", test_data["author"]["uuid"])
    assert output["name"] == "Tanaka Taro"
    assert output["uuid"] == test_data["author"]["uuid"]


def test_delete(app):
    with app.app_context():
        driver = get_driver()
        dao = AuthorDAO(driver)
        dao.register(
            test_data["author"]["name"],
            test_data["author"]["uuid"],
        )
        dao.delete(test_data["author"]["uuid"])
        result = dao.find(test_data["author"]["uuid"])
        assert result is None


def test_find(register_test_data):
    driver = get_driver()
    dao = AuthorDAO(driver)
    output = dao.find(test_data["author"]["uuid"])
    assert output["name"] == test_data["author"]["name"]
