from flask import Blueprint, current_app, render_template

from app.dao.books import BookDAO
from app.dao.pagination import (
    get_limit,
    get_page_num,
    get_pagination_num,
    get_start_index,
)

book_routes = Blueprint("books", __name__, url_prefix="/books")


@book_routes.get("/")
def get_index():
    dao = BookDAO(current_app.driver)

    page_num = get_page_num()
    limit = get_limit()
    start_index = get_start_index(page_num, limit)
    total_num = dao.get_total_count()
    pagination_num = get_pagination_num(total_num, limit)

    books = dao.all(start_index, limit)

    return render_template(
        "books.html",
        books=books,
        current_page=page_num,
        total_num=total_num,
        pagination_num=pagination_num,
        limit=limit,
    )


@book_routes.get("/<id>/")
def get_detail(id):
    dao = BookDAO(current_app.driver)
    book = dao.detail(id)
    related_books = dao.relate(id)

    if book:
        return render_template(
            "book-detail.html",
            book=book,
            related_books=related_books,
        )
    return render_template("book-not-found.html")
