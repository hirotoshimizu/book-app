class PublisherDAO:
    def __init__(self, driver):
        self.driver = driver

    def delete(self, name: str):
        def delete_genre(tx):
            return tx.run(
                "MATCH (p:Publisher {name: $name}) DETACH DELETE p", name=name
            )

        with self.driver.session() as session:
            return session.execute_write(delete_genre)
