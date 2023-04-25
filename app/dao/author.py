class AuthorDAO:
    def __init__(self, driver):
        self.driver = driver

    def wrote(self):
        def get_wrote_books(tx):
            result = tx.run("MATCH (n:Book) RETURN n")
            return [i.value(0) for i in result]

        with self.driver.session() as session:
            return session.execute_read(get_books)

    def delete(self, name: str):
        def delete_author(tx):
            return tx.run(
                "MATCH (a:Author {name: $name}) DETACH DELETE a", name=name
            ).consume()

        with self.driver.session() as session:
            return session.execute_write(delete_author)
