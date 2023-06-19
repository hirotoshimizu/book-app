import pytest

from app.dao.tag import TagDAO
from app.exceptions.validation import ValidationException
from app.neo4j import get_driver
from app.tests.conftest import test_data


def test_all(register_test_data):
    driver = get_driver()
    dao = TagDAO(driver)
    result = dao.all()
    assert test_data["tag"]["name"] in str(result)


def test_register(app):
    with app.app_context():
        driver = get_driver()
        dao = TagDAO(driver)

        dao.register(test_data["tag"]["name"], test_data["genre"]["uuid"])
        result = dao.find(test_data["genre"]["uuid"])
        dao.delete(test_data["genre"]["uuid"])

        assert result["name"] == test_data["tag"]["name"]


def test_validation_error(register_test_data):
    driver = get_driver()
    dao = TagDAO(driver)

    with pytest.raises(ValidationException):
        dao.register(test_data["tag"]["name"], test_data["tag"]["uuid"])


def test_update(register_test_data):
    driver = get_driver()
    dao = TagDAO(driver)
    output = dao.update("TEST-TAG", test_data["tag"]["uuid"])
    assert output["name"] == "TEST-TAG"
    assert output["uuid"] == test_data["tag"]["uuid"]


def test_delete(app):
    with app.app_context():
        driver = get_driver()
        dao = TagDAO(driver)
        dao.register(
            test_data["tag"]["name"],
            test_data["tag"]["uuid"],
        )
        dao.delete(test_data["tag"]["uuid"])
        result = dao.find(test_data["tag"]["uuid"])
        assert result is None


def test_find(register_test_data):
    driver = get_driver()
    dao = TagDAO(driver)
    output = dao.find(test_data["tag"]["uuid"])
    assert output["name"] == test_data["tag"]["name"]
