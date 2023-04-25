class GenreDAO:
    def __init__(self, driver):
        self.driver = driver

    def all(self):
        def get_genres(tx):
            result = tx.run("MATCH (n:Genre) RETURN n")
            return [r.value(0) for r in result]

        with self.driver.session() as session:
            return session.execute_read(get_genres)

    def register(self, name, name_en):
        def create_genre(tx, name, name_en):
            return tx.run(
                """
                CREATE (g:Genre {
                    name: $name,
                    name_en: $name_en
                })
                RETURN g""",
                name=name,
                name_en=name_en,
            ).single()

        with self.driver.session() as session:
            result = session.execute_write(create_genre, name, name_en)
            genre = result["g"]

            payload = {
                "name": genre["name"],
                "name_en": genre["name_en"],
            }
            return payload

    def delete(self, name: str):
        def delete_genre(tx):
            return tx.run("MATCH (g:Genre {name: $name}) DETACH DELETE g", name=name)

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

    def find(self, name_en: str):
        def find_genre(tx, name_en):
            result = tx.run(
                "MATCH (g:Genre {name_en: $name_en}) return g AS name", name_en=name_en
            ).single()
            if not result:
                return None
            return result.get("name")

        with self.driver.session() as session:
            return session.execute_read(find_genre, name_en)
