import bcrypt
from flask_login import UserMixin
from neo4j.exceptions import ConstraintError

from app.exceptions.validation import ValidationException


class User(UserMixin):
    def __init__(self, email: str, name: str) -> None:
        self.id = email
        self.name = name


class UserDAO:
    def __init__(self, driver):
        self.driver = driver

    def register(self, email, plain_password, name):
        encrypted = bcrypt.hashpw(
            plain_password.encode("utf8"), bcrypt.gensalt()
        ).decode("utf8")

        def create_user(tx, email, encrypted, name):
            return tx.run(
                """
                CREATE (u:User {
                    userId: randomUuid(),
                    email: $email,
                    password: $encrypted,
                    name: $name
                })
                RETURN u
            """,
                email=email,
                encrypted=encrypted,
                name=name,
            ).single()

        try:
            with self.driver.session() as session:
                result = session.execute_write(create_user, email, encrypted, name)
                user = result["u"]

                created_user = User(user["email"], user["name"])

                return created_user

        except ConstraintError as err:
            raise ValidationException(err.message, {"email": err.message})

    def authenticate(self, email, plain_password):
        def get_user(tx, email):
            result = tx.run("MATCH (u:User {email: $email}) RETURN u", email=email)
            first = result.single()

            if first is None:
                return None

            user = first.get("u")
            return user

        with self.driver.session() as session:
            record = session.execute_read(get_user, email=email)

            if record is None:
                return False

            if (
                bcrypt.checkpw(
                    plain_password.encode("utf-8"), record["password"].encode("utf-8")
                )
                is False
            ):
                return False

            return User(record["email"], record["name"])

    def find(self, email: str):
        def find_user(tx, email):
            result = tx.run("MATCH (u:User {email: $email}) RETURN u", email=email)
            first = result.single()

            if first is None:
                return None

            user = first.get("u")

            return User(user["email"], user["name"])

        with self.driver.session() as session:
            return session.execute_read(find_user, email=email)
