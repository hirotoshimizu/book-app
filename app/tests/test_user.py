import os

import pytest

from app.dao.user import UserDAO
from app.exceptions.validation import ValidationException
from app.neo4j import get_driver

email = "test@gmail.com"
password = "password"
name = "John Smith"


@pytest.fixture()
def before_all(app):
    with app.app_context():
        driver = get_driver()

        def delete_user(tx):
            return tx.run(
                "MATCH (u:User {email: $email}) DETACH DELETE u", email=email
            ).consume()

        with driver.session() as session:
            session.execute_write(delete_user)
            session.close()


def test_unique_constraint(before_all, app):
    def get_constraints(tx):
        return tx.run(
            """
            SHOW CONSTRAINTS
            YIELD name, labelsOrTypes, properties
            WHERE labelsOrTypes = ['User'] AND properties = ['email']
            RETURN *
        """
        ).single()

    with app.app_context():
        with get_driver().session() as session:
            res = session.execute_read(get_constraints)

            assert res is not None


def test_register_user(before_all, app):
    with app.app_context():
        driver = get_driver()

        dao = UserDAO(driver)

        user = dao.register(email, password, name)

        assert user.id == email
        assert user.name == name


def test_validation_error(before_all, app):
    with app.app_context():
        driver = get_driver()

        dao = UserDAO(driver)

        dao.register(email, password, name)

        with pytest.raises(ValidationException):
            dao.register(email, password, name)


def test_authenticate_user(app):
    with app.app_context():
        driver = get_driver()

        def delete_user(tx):
            return tx.run(
                "MATCH (u:User {email: $email}) DETACH DELETE u", email=email
            ).consume()

        with driver.session() as session:
            session.execute_write(delete_user)
            session.close()

        dao = UserDAO(driver)

        dao.register(email, password, name)

        output = dao.authenticate(email, password)

        assert output.name == name
        assert output.is_authenticated == True


def test_return_false_incorrect_password(app):
    with app.app_context():
        driver = get_driver()

        dao = UserDAO(driver)

        output = dao.authenticate(email, "random_password")

        assert output is False


def test_return_false_incorrect_username(app):
    with app.app_context():
        driver = get_driver()

        dao = UserDAO(driver)

        output = dao.authenticate("unknown@email.com", password)

        assert output is False


def test_set_GA_timestamp_to_verify_test(app):
    def update_user(tx):
        return tx.run(
            """
            MATCH (u:User {email: $email})
            SET u.authenticatedAt = datetime()
        """,
            email=email,
        ).consume()

    with app.app_context():
        driver = get_driver()

        with driver.session() as session:
            session.execute_write(update_user)
