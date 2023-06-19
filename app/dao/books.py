from dataclasses import dataclass

from neo4j.exceptions import ConstraintError

from app.exceptions.validation import ValidationException


@dataclass
class Book:
    book_id: str
    title: str
    sub_title: str
    summary: str
    publication_year: int
    edition: int
    url: str
    image: str
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

    def register(self, Book, genre, tags, publisher, authors):
        def create_book(tx, Book):
            return tx.run(
                """
                CREATE (b:Book {
                    book_id: $book_id,
                    title: $title,
                    sub_title: $sub_title,
                    summary: $summary,
                    publication_year: $publication_year,
                    edition: $edition,
                    url: $url,
                    image: $image,
                    created_at: $created_at
                })
                WITH b
                MATCH (g:Genre {name: $genre}) 
                MERGE (b)-[:IN_GENRE]->(g) 
                WITH b
                UNWIND $tag_name AS tag 
                MERGE (t:Tag {name: tag}) 
                MERGE (b)-[:HAS_TAG]->(t)
                WITH b
                MERGE (p:Publisher {name: $publisher}) 
                MERGE (p)-[:PUBLISHED]->(b)
                WITH b
                UNWIND $authors AS author 
                MERGE (a:Author {name: author}) 
                MERGE (a)-[:WROTE]->(b)
                RETURN b""",
                book_id=Book.book_id,
                title=Book.title,
                sub_title=Book.sub_title,
                summary=Book.summary,
                publication_year=Book.publication_year,
                edition=Book.edition,
                url=Book.url,
                image=Book.image,
                created_at=Book.created_at,
                genre=genre,
                tag_name=tags,
                publisher=publisher,
                authors=authors,
            ).single()

        # with self.driver.session() as session:
        #     return session.execute_write(create_book, Book)
        try:
            with self.driver.session() as session:
                result = session.execute_write(create_book, Book)
                print(f"result%%%%%%%%%%% {result}")
                return result
        except ConstraintError as err:
            raise ValidationException(err.message, {"book_id": err.message})

    def update(self, Book, genre, tags, publisher, authors):
        def update_book(tx, Book):
            result = tx.run(
                """
                MATCH (b:Book {book_id: $book_id})
                SET
                b.title = $title, b.sub_title = $sub_title,
                b.summary = $summary, b.edition = $edition,
                b.publication_year = $publication_year,
                b.url = $url, b.created_at = $created_at
                WITH b
                MATCH (a:Author) - [rw:WROTE] -> (b:Book)
                DELETE rw
                WITH b
                UNWIND $authors AS author 
                MATCH (a2:Author {name: author})
                MERGE (a2)-[:WROTE]->(b)
                WITH b
                MATCH (b) - [hr:HAS_TAG] -> (t:Tag)
                DELETE hr
                WITH b
                UNWIND $tag_name AS tag 
                MATCH (t2:Tag {name: tag})
                MERGE (b)-[:HAS_TAG]->(t2)
                WITH b
                MATCH (b) - [r:IN_GENRE] -> (g:Genre)
                DELETE r
                WITH b
                MATCH (g2:Genre {name: $genre})
                MERGE (b)-[r1:IN_GENRE]->(g2)
                WITH DISTINCT 1 as ignored
                MATCH (p:Publisher) - [rp:PUBLISHED] -> (b1:Book {book_id: $book_id})
                MATCH (p2:Publisher {name: $publisher})
                WHERE NOT (p.name = $publisher) 
                MERGE (p2) -[rp1:PUBLISHED] -> (b1)
                WITH rp
                DELETE rp
                """,
                book_id=Book.book_id,
                title=Book.title,
                sub_title=Book.sub_title,
                summary=Book.summary,
                publication_year=Book.publication_year,
                edition=Book.edition,
                image=Book.image,
                url=Book.url,
                created_at=Book.created_at,
                genre=genre,
                tag_name=tags,
                publisher=publisher,
                authors=authors,
            ).single()

        try:
            with self.driver.session() as session:
                return session.execute_write(update_book, Book)
        except ConstraintError as err:
            raise ValidationException(err.message, {"detail": err.message})

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
                   OPTIONAL MATCH (b)-[:IN_GENRE]->(g:Genre)
                   OPTIONAL MATCH (p:Publisher)-[:PUBLISHED]->(b)
                   OPTIONAL MATCH (b)-[:HAS_TAG]->(t:Tag)
                   RETURN b, 
                   COLLECT(DISTINCT a.name) AS authors, 
                   COLLECT(DISTINCT t.name) AS tags, 
                   g.name AS genre,
                   p.name AS publisher""",
                id=id,
            )
            if not result:
                return None
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
