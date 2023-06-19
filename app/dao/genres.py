from neo4j.exceptions import ConstraintError

from app.exceptions.validation import ValidationException


class GenreDAO:
    def __init__(self, driver):
        self.driver = driver

    def all(self):
        def get_genres(tx):
            result = tx.run("MATCH (n:Genre) RETURN n ORDER BY n.name")
            return [r.value(0) for r in result]

        with self.driver.session() as session:
            return session.execute_read(get_genres)

    def register(self, name: str, name_en: str, uuid: str):
        def create_genre(tx, name, name_en, uuid):
            return tx.run(
                """
                CREATE (g:Genre {
                    name: $name,
                    name_en: $name_en,
                    uuid: $uuid
                })
                RETURN g""",
                name=name,
                name_en=name_en,
                uuid=uuid,
            ).single()

        try:
            with self.driver.session() as session:
                result = session.execute_write(create_genre, name, name_en, uuid)

                genre = result["g"]
                payload = {
                    "name": genre["name"],
                    "name_en": genre["name_en"],
                }

                return payload
        except ConstraintError as err:
            raise ValidationException(err.message, {"detail": err.message})

    def update(self, name: str, name_en: str, uuid: str):
        def update_genre(tx, name: str, name_en: str, uuid: str):
            # return tx.run(
            #     """
            #     MATCH (g:Genre {uuid: $uuid})
            #     SET g.name = $name, g.name_en = $name_en
            #     RETURN g""",
            #     uuid=uuid,
            #     name=name,
            #     name_en=name_en,
            # ).single()
            result = tx.run(
                """
                MATCH (g:Genre {uuid: $uuid})
                SET g.name = $name, g.name_en = $name_en
                RETURN g""",
                uuid=uuid,
                name=name,
                name_en=name_en,
            ).single()
            return result[0]

        with self.driver.session() as session:
            return session.execute_write(update_genre, name, name_en, uuid)

    def delete(self, uuid: str):
        def delete_genre(tx):
            return tx.run("MATCH (g:Genre {uuid: $uuid}) DETACH DELETE g", uuid=uuid)

        with self.driver.session() as session:
            return session.execute_write(delete_genre)

    def get_by_genre(self, name_en: str, skip=0, limit=9):
        def get_books_in_genre(tx, name_en: str, skip=0, limit=9):
            result = tx.run(
                """
                MATCH (b:Book)-[r:IN_GENRE]->(g:Genre {name_en: $name_en})
                MATCH (a:Author)-[:WROTE]->(b:Book)
                WITH b, g, collect(a) AS authors
                RETURN b, authors
                ORDER BY b.created_at DESC 
                SKIP $skip
                LIMIT $limit
            """,
                name_en=name_en,
                skip=skip,
                limit=limit,
            )
            return [b for b in result]

        with self.driver.session() as session:
            return session.execute_read(get_books_in_genre, name_en, skip, limit)

    def get_by_genre_total_count(self, name_en: str):
        def get_count_books_in_genre(tx, name_en):
            result = tx.run(
                "MATCH (b:Book)-[r:IN_GENRE]->(g:Genre {name_en: $name_en}) RETURN count(*)",
                name_en=name_en,
            ).single()
            return result[0]

        with self.driver.session() as session:
            return session.execute_read(get_count_books_in_genre, name_en)

    # def find(self, name_en: str):
    #     def find_genre(tx, name_en):
    #         result = tx.run(
    #             "MATCH (g:Genre {name_en: $name_en}) return g AS name", name_en=name_en
    #         ).single()
    #         if not result:
    #             return None
    #         return result.get("name")

    #     with self.driver.session() as session:
    #         return session.execute_read(find_genre, name_en)

    def find(self, uuid: str):
        def find_genre(tx, uuid):
            result = tx.run(
                "MATCH (g:Genre {uuid: $uuid}) return g AS name", uuid=uuid
            ).single()
            if not result:
                return None
            return result.get("name")

        with self.driver.session() as session:
            return session.execute_read(find_genre, uuid)

    def find_by_name(self, name: str):
        def find_genre_by_name(tx, name):
            result = tx.run(
                "MATCH (g:Genre {name: $name}) return g AS name", name=name
            ).single()
            if not result:
                return None
            return result.get("name")

        with self.driver.session() as session:
            return session.execute_read(find_genre_by_name, name)

    def find_by_name_en(self, name_en: str):
        def find_genre_by_name_en(tx, name_en):
            result = tx.run(
                "MATCH (g:Genre {name_en: $name_en}) return g AS name_en",
                name_en=name_en,
            ).single()
            if not result:
                return None
            return result.get("name_en")

        with self.driver.session() as session:
            return session.execute_read(find_genre_by_name_en, name_en)
