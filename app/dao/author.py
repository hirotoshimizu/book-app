from neo4j.exceptions import ConstraintError

from app.exceptions.validation import ValidationException


class AuthorDAO:
    def __init__(self, driver):
        self.driver = driver

    def all(self):
        def get_authors(tx):
            result = tx.run("MATCH (n:Author) RETURN n ORDER BY n.name")
            return [r.value(0) for r in result]

        with self.driver.session() as session:
            return session.execute_read(get_authors)

    def register(self, name, uuid):
        def create_author(tx, name, uuid):
            return tx.run(
                """
                CREATE (a:Author {
                    name: $name,
                    uuid: $uuid
                })
                RETURN a""",
                name=name,
                uuid=uuid,
            ).single()

        try:
            with self.driver.session() as session:
                result = session.execute_write(create_author, name, uuid)

                genre = result["a"]
                payload = {"name": genre["name"], "uuid": genre["uuid"]}

                return payload
        except ConstraintError as err:
            raise ValidationException(err.message, {"name": err.message})

    def update(self, name: str, uuid: str):
        def update_author(tx, name: str, uuid: str):
            result = tx.run(
                """
                MATCH (a:Author {uuid: $uuid})
                SET a.name = $name
                RETURN a""",
                uuid=uuid,
                name=name,
            ).single()
            return result[0]

        with self.driver.session() as session:
            return session.execute_write(update_author, name, uuid)

    def wrote(self):
        def get_wrote_books(tx):
            result = tx.run("MATCH (n:Book) RETURN n")
            return [i.value(0) for i in result]

        with self.driver.session() as session:
            return session.execute_read(get_books)

    def delete(self, uuid: str):
        def delete_author(tx):
            return tx.run(
                "MATCH (a:Author {uuid: $uuid}) DETACH DELETE a", uuid=uuid
            ).consume()

        with self.driver.session() as session:
            return session.execute_write(delete_author)

    def find(self, uuid: str):
        def find_author(tx, uuid):
            result = tx.run(
                "MATCH (a:Author {uuid: $uuid}) return a AS name", uuid=uuid
            ).single()
            if not result:
                return None
            return result.get("name")

        with self.driver.session() as session:
            return session.execute_read(find_author, uuid)

    def find_by_name(self, name: str):
        def find_author_by_name(tx, name):
            result = tx.run(
                "MATCH (a:Author {name: $name}) return a AS name", name=name
            ).single()
            if not result:
                return None
            return result.get("name")

        with self.driver.session() as session:
            return session.execute_read(find_author_by_name, name)
