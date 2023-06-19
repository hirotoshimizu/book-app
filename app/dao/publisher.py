from neo4j.exceptions import ConstraintError

from app.exceptions.validation import ValidationException


class PublisherDAO:
    def __init__(self, driver):
        self.driver = driver

    def all(self):
        def get_publishers(tx):
            result = tx.run("MATCH (n:Publisher) RETURN n ORDER BY n.name")
            return [r.value(0) for r in result]

        with self.driver.session() as session:
            return session.execute_read(get_publishers)

    def register(self, name, uuid):
        def create_publisher(tx, name, uuid):
            return tx.run(
                """
                CREATE (p:Publisher {
                    name: $name,
                    uuid: $uuid
                })
                RETURN p""",
                name=name,
                uuid=uuid,
            ).single()

        try:
            with self.driver.session() as session:
                result = session.execute_write(create_publisher, name, uuid)

                genre = result["p"]
                payload = {"name": genre["name"], "uuid": genre["uuid"]}

                return payload
        except ConstraintError as err:
            raise ValidationException(err.message, {"detail": err.message})

    def update(self, name: str, uuid: str):
        def update_publisher(tx, name: str, uuid: str):
            result = tx.run(
                """
                MATCH (p:Publisher {uuid: $uuid})
                SET p.name = $name
                RETURN p""",
                uuid=uuid,
                name=name,
            ).single()
            return result[0]

        with self.driver.session() as session:
            return session.execute_write(update_publisher, name, uuid)

    def delete(self, uuid: str):
        def delete_publisher(tx):
            return tx.run(
                "MATCH (p:Publisher {uuid: $uuid}) DETACH DELETE p", uuid=uuid
            )

        with self.driver.session() as session:
            return session.execute_write(delete_publisher)

    def find(self, uuid: str):
        def find_publisher(tx, uuid):
            result = tx.run(
                "MATCH (p:Publisher {uuid: $uuid}) return p AS name", uuid=uuid
            ).single()
            if not result:
                return None
            return result.get("name")

        with self.driver.session() as session:
            return session.execute_read(find_publisher, uuid)

    def find_by_name(self, name: str):
        def find_publisher_by_name(tx, name):
            result = tx.run(
                "MATCH (p:Publisher {name: $name}) return p AS name", name=name
            ).single()
            if not result:
                return None
            return result.get("name")

        with self.driver.session() as session:
            return session.execute_read(find_publisher_by_name, name)
