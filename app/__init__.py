import os

from flask import Flask, abort, current_app, render_template, request
from flask_login import LoginManager

from app.dao.books import BookDAO
from app.dao.genres import GenreDAO
from app.dao.pagination import (
    get_limit,
    get_page_num,
    get_pagination_num,
    get_start_index,
)
from app.dao.user import UserDAO

from .forms.admin import forms_routes
from .neo4j import init_driver
from .routes.admin import admin_routes

# from .routes.auth import auth_routes
from .routes.books import book_routes
from .routes.genres import genre_routes
from .routes.graphs import graph_routes


def create_app(test_config=None):
    static_folder = os.path.join(os.path.dirname(__file__), "..", "public")
    app = Flask(__name__, static_url_path="/", static_folder=static_folder)

    app.config["UPLOAD_FOLDER"] = os.path.join(static_folder, "images", "books")
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET")

    app.config.from_mapping(
        NEO4J_URI=os.getenv("NEO4J_URI"),
        NEO4J_USERNAME=os.getenv("NEO4J_USERNAME"),
        NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD"),
        # NEO4J_DATABASE=os.getenv("NEO4J_DATABASE"),
    )

    if test_config is not None:
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        init_driver(
            app.config.get("NEO4J_URI"),
            app.config.get("NEO4J_USERNAME"),
            app.config.get("NEO4J_PASSWORD"),
        )

    app.register_blueprint(admin_routes)
    # app.register_blueprint(auth_routes)
    app.register_blueprint(book_routes)
    app.register_blueprint(genre_routes)
    app.register_blueprint(graph_routes)
    app.register_blueprint(forms_routes)

    login_maneger = LoginManager()
    login_maneger.loginview = "admin.book"
    login_maneger.init_app(app)

    @login_maneger.user_loader
    def load_user(user_id):
        dao = UserDAO(current_app.driver)
        return dao.find(user_id)

    @app.route("/")
    def index():
        dao = BookDAO(current_app.driver)
        output = dao.latest(6)
        return render_template("index.html", objects=output)

    @app.route("/search")
    def search():
        search_word = request.args.get("q", "")
        dao = BookDAO(current_app.driver)

        page_num = get_page_num()
        limit = get_limit()
        start_index = get_start_index(page_num, limit)
        total_num = dao.get_search_count(search_word)
        pagination_num = get_pagination_num(total_num, limit)

        books = dao.search(search_word, start_index, limit)

        return render_template(
            "search.html",
            books=books,
            search_word=search_word,
            current_page=page_num,
            total_num=total_num,
            pagination_num=pagination_num,
            limit=limit,
        )

    @app.context_processor
    def header_genres():
        dao = GenreDAO(current_app.driver)
        output = dao.all()
        return dict(genres=output)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html")

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Server error: {e}. route: {request.url}")
        return render_template("500.html")

    return app
