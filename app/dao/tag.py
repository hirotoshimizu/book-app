from neo4j.exceptions import ConstraintError

from app.exceptions.validation import ValidationException


class TagDAO:
    def __init__(self, driver):
        self.driver = driver

    def all(self):
        def get_tags(tx):
            result = tx.run("MATCH (n:Tag) RETURN n ORDER BY n.name")
            return [r.value(0) for r in result]

        with self.driver.session() as session:
            return session.execute_read(get_tags)

    def register(self, name, uuid):
        def create_tag(tx, name, uuid):
            return tx.run(
                """
                CREATE (t:Tag {
                    name: $name,
                    uuid: $uuid
                })
                RETURN t""",
                name=name,
                uuid=uuid,
            ).single()

        try:
            with self.driver.session() as session:
                result = session.execute_write(create_tag, name, uuid)

                tag = result["t"]
                payload = {"name": tag["name"], "uuid": tag["uuid"]}

                return payload
        except ConstraintError as err:
            raise ValidationException(err.message, {"detail": err.message})

    def update(self, name: str, uuid: str):
        def update_tag(tx, name: str, uuid: str):
            result = tx.run(
                """
                MATCH (t:Tag {uuid: $uuid})
                SET t.name = $name
                RETURN t""",
                uuid=uuid,
                name=name,
            ).single()
            return result[0]

        with self.driver.session() as session:
            return session.execute_write(update_tag, name, uuid)

    def delete(self, uuid: str):
        def delete_genre(tx):
            return tx.run("MATCH (t:Tag {uuid: $uuid}) DETACH DELETE t", uuid=uuid)

        with self.driver.session() as session:
            return session.execute_write(delete_genre)

    def find(self, uuid: str):
        def find_tag(tx, uuid):
            result = tx.run(
                "MATCH (t:Tag {uuid: $uuid}) return t AS name", uuid=uuid
            ).single()
            if not result:
                return None
            return result.get("name")

        with self.driver.session() as session:
            return session.execute_read(find_tag, uuid)

    def find_by_name(self, name: str):
        def find_tag_by_name(tx, name):
            result = tx.run(
                "MATCH (t:Tag {name: $name}) return t AS name", name=name
            ).single()
            if not result:
                return None
            return result.get("name")

        with self.driver.session() as session:
            return session.execute_read(find_tag_by_name, name)
