class TagDAO:
    def __init__(self, driver):
        self.driver = driver

    def delete(self, name: str):
        def delete_genre(tx):
            return tx.run("MATCH (t:Tag {name: $name}) DETACH DELETE t", name=name)

        with self.driver.session() as session:
            return session.execute_write(delete_genre)
