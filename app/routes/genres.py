from flask import Blueprint, current_app, render_template, request

from app.dao.genres import GenreDAO
from app.dao.pagination import (
    get_limit,
    get_page_num,
    get_pagination_num,
    get_start_index,
)

genre_routes = Blueprint("genre", __name__, url_prefix="/genres")


@genre_routes.get("/<name_en>/")
def get_genre(name_en):

    dao = GenreDAO(current_app.driver)

    title = dao.find(name_en)

    page_num = get_page_num()
    limit = get_limit()
    start_index = get_start_index(page_num, limit)
    total_num = dao.get_by_genre_total_count(name_en)
    pagination_num = get_pagination_num(total_num, limit)

    books = dao.get_by_genre(name_en, start_index, limit)

    return render_template(
        "books.html",
        title=title,
        books=books,
        current_page=page_num,
        total_num=total_num,
        pagination_num=pagination_num,
        limit=limit,
    )
