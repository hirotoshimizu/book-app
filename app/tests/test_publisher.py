import pytest

from app.dao.publisher import PublisherDAO
from app.exceptions.validation import ValidationException
from app.neo4j import get_driver
from app.tests.conftest import test_data


def test_all(register_test_data):
    driver = get_driver()
    dao = PublisherDAO(driver)

    result = dao.all()

    assert test_data["publisher"]["name"] in str(result)


def test_register(app):
    with app.app_context():
        driver = get_driver()
        dao = PublisherDAO(driver)
        dao.register(test_data["publisher"]["name"], test_data["publisher"]["uuid"])
        result = dao.find(test_data["publisher"]["uuid"])
        dao.delete(test_data["publisher"]["uuid"])

        assert result["name"] == test_data["publisher"]["name"]


def test_validation_error(register_test_data):
    driver = get_driver()
    dao = PublisherDAO(driver)

    with pytest.raises(ValidationException):
        dao.register(test_data["publisher"]["name"], test_data["publisher"]["uuid"])


def test_update(register_test_data):
    driver = get_driver()
    dao = PublisherDAO(driver)
    output = dao.update("TEST_PUBLISHER", test_data["publisher"]["uuid"])
    assert output["name"] == "TEST_PUBLISHER"
    assert output["uuid"] == test_data["publisher"]["uuid"]


def test_delete(app):
    with app.app_context():
        driver = get_driver()
        dao = PublisherDAO(driver)
        dao.register(
            test_data["publisher"]["name"],
            test_data["publisher"]["uuid"],
        )
        dao.delete(test_data["publisher"]["uuid"])
        result = dao.find(test_data["publisher"]["uuid"])
        assert result is None


def test_find(register_test_data):
    driver = get_driver()
    dao = PublisherDAO(driver)
    output = dao.find(test_data["publisher"]["uuid"])
    assert output["name"] == test_data["publisher"]["name"]
