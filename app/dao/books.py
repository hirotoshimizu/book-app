from dataclasses import dataclass


@dataclass
class Book:
    book_id: str
    title: str
    sub_title: str
    summary: str
    publication_year: int
    edition: int
    url: str
    created_at: int


class BookDAO:
    def __init__(self, driver):
        self.driver = driver

    def all(self, skip=0, limit=9):
        def get_books(tx, skip, limit):
            result = tx.run(
                """
                MATCH (a:Author)-[:WROTE]->(b:Book) 
                WITH b, collect(a) AS authors 
                RETURN b, authors 
                ORDER BY b.created_at 
                DESC SKIP $skip
                LIMIT $limit""",
                skip=skip,
                limit=limit,
            )
            return [b for b in result]

        with self.driver.session() as session:
            return session.execute_read(get_books, skip, limit)

    def register(self, Book, genre, tag, publisher, author):
        def create_book(tx, Book):
            return tx.run(
                """
                MERGE (b:Book {
                    book_id: $book_id,
                    title: $title,
                    sub_title: $sub_title,
                    summary: $summary,
                    publication_year: $publication_year,
                    edition: $edition,
                    url: $url,
                    created_at: $created_at
                })
                WITH b
                MATCH (g:Genre {name: $genre}) 
                MERGE (b)-[:IN_GENRE]->(g) 
                WITH b
                MERGE (t:Tag {name: $tag_name}) 
                MERGE (b)-[:HAS_TAG]->(t)
                WITH b
                MERGE (p:Publisher {name: $publisher}) 
                MERGE (p)-[:PUBLISHED]->(b)
                WITH b
                MERGE (a:Author {name: $author_name}) 
                MERGE (a)-[:WROTE]->(b)
                RETURN b""",
                book_id=Book.book_id,
                title=Book.title,
                sub_title=Book.sub_title,
                summary=Book.summary,
                publication_year=Book.publication_year,
                edition=Book.edition,
                url=Book.url,
                created_at=Book.created_at,
                genre=genre,
                tag_name=tag,
                publisher=publisher,
                author_name=author,
            ).single()

        with self.driver.session() as session:
            return session.execute_write(create_book, Book)

    def delete(self, book_id: str):
        def delete_book(tx):
            return tx.run(
                "MATCH (b:Book {book_id: $book_id}) DETACH DELETE b", book_id=book_id
            ).consume()

        with self.driver.session() as session:
            return session.execute_write(delete_book)

    def get_total_count(self):
        def get_count_books(tx):
            result = tx.run("MATCH (b:Book) RETURN count(*)")
            return result.single()[0]

        with self.driver.session() as session:
            return session.execute_read(get_count_books)

    def latest(self, limit: int):
        def get_latest_books(tx, limit):
            result = tx.run(
                """
                MATCH (a:Author)-[:WROTE]->(b:Book) 
                WITH b, collect(a) AS authors 
                RETURN b, authors 
                ORDER BY b.created_at 
                DESC
                LIMIT $limit""",
                limit=limit,
            )
            return [b for b in result]

        with self.driver.session() as session:
            return session.execute_read(get_latest_books, limit)

    def detail(self, id: int):
        def get_book_detail(tx, id):
            result = tx.run(
                """MATCH (b:Book {book_id: $id}) 
                   OPTIONAL MATCH (a:Author)-[:WROTE]->(b)
                   OPTIONAL MATCH (p:Publisher)-[:PUBLISHED]->(b)
                   RETURN b, COLLECT(DISTINCT a.name) AS authors, p.name AS publisher""",
                id=id,
            )
            return result.single()

        with self.driver.session() as session:
            return session.execute_read(get_book_detail, id)

    def relate(self, id: int):
        def get_related_books(tx, id):
            result = tx.run(
                """
                MATCH (b:Book)-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(related_book:Book)<-[:WROTE]-(a:Author)
                WITH  b, related_book, collect(DISTINCT a) AS authors 
                WHERE b.book_id = $id
                RETURN DISTINCT related_book, authors""",
                id=id,
            )
            return [b for b in result]

        with self.driver.session() as session:
            return session.execute_read(get_related_books, id)

    def search(self, word: str, skip=0, limit=9):
        def search_books(tx, word, skip, limit):
            result = tx.run(
                """MATCH (a:Author)-[:WROTE]->(b:Book)
                WHERE toLower(b.title) CONTAINS toLower($word)
                OR toLower(b.sub_title) CONTAINS toLower($word)
                OR toLower(b.book_id) CONTAINS toLower($word)
                OR toLower(a.name) CONTAINS toLower($word)
                WITH b, collect(a) AS authors
                RETURN b, authors
                ORDER BY b.created_at
                DESC SKIP $skip
                LIMIT $limit""",
                word=word,
                skip=skip,
                limit=limit,
            )
            return [b for b in result]

        with self.driver.session() as session:
            return session.execute_read(search_books, word, skip, limit)

    def get_search_count(self, word: str):
        def get_count_books(tx, word):
            result = tx.run(
                """MATCH (a:Author)-[:WROTE]->(b:Book) 
                WHERE toLower(b.title) CONTAINS toLower($word)
                OR toLower(b.sub_title) CONTAINS toLower($word)
                OR toLower(b.book_id) CONTAINS toLower($word)
                OR toLower(a.name) CONTAINS toLower($word)
                WITH b, collect(a) AS authors 
                RETURN count(b)""",
                word=word,
            )
            return result.single()[0]

        with self.driver.session() as session:
            return session.execute_read(get_count_books, word)
