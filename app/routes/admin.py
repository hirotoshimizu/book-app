import os
import time
import uuid

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from app.dao.author import AuthorDAO
from app.dao.books import Book, BookDAO
from app.dao.genres import GenreDAO
from app.dao.pagination import get_page_num, get_pagination_num, get_start_index
from app.dao.publisher import PublisherDAO
from app.dao.tag import TagDAO
from app.dao.user import UserDAO
from app.exceptions.validation import ValidationException
from app.forms.admin import (
    AuthorRegistrationForm,
    AuthorUpdateForm,
    BookRegistrationForm,
    BookUpdateForm,
    GenreRegistrationForm,
    GenreUpdateForm,
    LoginForm,
    PublisherRegistrationForm,
    PublisherUpdateForm,
    TagRegistrationForm,
    TagUpdateForm,
)

admin_routes = Blueprint("admin", __name__, url_prefix="/admin")


allowed_extensions = {"png", "jpg", "jpeg"}

unix_timestamp = int(time.time())


def get_extension(filename):
    return filename.rsplit(".", 1)[1]


def allowed_file(filename):
    return "." in filename and get_extension(filename).lower() in allowed_extensions


def genrerate_uuid() -> str:
    new_uuid = uuid.uuid4()
    return str(new_uuid)


@admin_routes.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("admin/index.html")


@admin_routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


@admin_routes.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        dao = UserDAO(current_app.driver)
        email = form.email.data
        password = form.password.data
        user = dao.authenticate(email, password)
        login_user(user, remember=True)
        return redirect(url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin_routes.route("/books", methods=["GET"])
@login_required
def books():
    dao = BookDAO(current_app.driver)
    page_num = get_page_num()
    # limit = get_limit()
    limit = 20
    start_index = get_start_index(page_num, limit)
    total_num = dao.get_total_count()
    pagination_num = get_pagination_num(total_num, limit)

    books = dao.all(start_index, limit)

    return render_template(
        "admin/books/index.html",
        books=books,
        current_page=page_num,
        total_num=total_num,
        pagination_num=pagination_num,
        limit=limit,
    )


@admin_routes.route("/book/register", methods=["GET", "POST"])
@login_required
def book_create():
    dao = BookDAO(current_app.driver)
    author_dao = AuthorDAO(current_app.driver)
    genre_dao = GenreDAO(current_app.driver)
    publisher_dao = PublisherDAO(current_app.driver)
    tag_dao = TagDAO(current_app.driver)
    authors, genres = author_dao.all(), genre_dao.all()
    publishers, tags = publisher_dao.all(), tag_dao.all()

    form = BookRegistrationForm()
    form.authors.choices = [(author["name"], author["name"]) for author in authors]
    form.genre.choices = [(genre["name"], genre["name"]) for genre in genres]
    form.publisher.choices = [
        (publisher["name"], publisher["name"]) for publisher in publishers
    ]
    form.tags.choices = [(tag["name"], tag["name"]) for tag in tags]
    if request.method == "POST" and form.validate_on_submit():
        file = request.files["file"]
        filename = ""
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        book = Book(
            book_id=form.book_id.data,
            title=form.title.data,
            sub_title=form.sub_title.data,
            summary=form.summary.data,
            publication_year=form.publication_year.data,
            edition=form.edition.data,
            url=form.url.data,
            image=filename,
            created_at=unix_timestamp,
        )
        dao.register(
            Book=book,
            genre=form.genre.data,
            tags=form.tags.data,
            publisher=form.publisher.data,
            authors=form.authors.data,
        )
        return redirect(url_for("admin.books"))
    return render_template(
        "admin/books/register.html",
        form=form,
    )

    # if request.method != "POST" and not form.validate_on_submit():
    #     return render_template(
    #         "admin/books/register.html",
    #         form=form,
    #     )
    # file = request.files["file"]
    # filename = ""
    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    # book = Book(
    #     book_id=form.book_id.data,
    #     title=form.title.data,
    #     sub_title=form.sub_title.data,
    #     summary=form.summary.data,
    #     publication_year=form.publication_year.data,
    #     edition=form.edition.data,
    #     url=form.url.data,
    #     image=filename,
    #     created_at=unix_timestamp,
    # )
    # dao.register(
    #     Book=book,
    #     genre=form.genre.data,
    #     tags=form.tags.data,
    #     publisher=form.publisher.data,
    #     authors=form.authors.data,
    # )
    # return redirect(url_for("admin.books"))

    # try:
    #     dao.register(
    #         Book=book,
    #         genre=form.genre.data,
    #         tags=form.tags.data,
    #         publisher=form.publisher.data,
    #         authors=form.authors.data,
    #     )
    #     return redirect(url_for("admin.books"))
    # except ValidationException:
    #     message = "book_id already exists."
    #     print(f"ValidationException.message {Exception.message}")
    #     return render_template("admin/books/register.html", form=form, message=message)


def get_image_and_path(img_path, img):
    img_path = "/".join(map(str, img_path[-2:]))
    img = (f"/{img_path}/{img}") if img else ""
    return img


@admin_routes.route("/books/<id>", methods=["GET", "POST"])
@login_required
def book_detail(id):
    dao = BookDAO(current_app.driver)
    author_dao = AuthorDAO(current_app.driver)
    genre_dao = GenreDAO(current_app.driver)
    publisher_dao = PublisherDAO(current_app.driver)
    tag_dao = TagDAO(current_app.driver)
    authors, genres = author_dao.all(), genre_dao.all()
    publishers, tags = publisher_dao.all(), tag_dao.all()

    book = dao.detail(id)
    upload_folder = os.path.join(current_app.config["UPLOAD_FOLDER"]).split("/")
    image = get_image_and_path(upload_folder, book["b"]["image"])

    form = BookUpdateForm(
        authors=book["authors"],
        book_id=book["b"]["book_id"],
        created_at=book["b"]["created_at"],
        genre=book["genre"],
        publisher=book["publisher"],
        publication_year=book["b"]["publication_year"],
        sub_title=book["b"]["sub_title"],
        summary=book["b"]["summary"],
        tags=book["tags"],
        title=book["b"]["title"],
        url=book["b"]["url"],
    )
    form.authors.choices = [(author["name"], author["name"]) for author in authors]
    form.genre.choices = [(genre["name"], genre["name"]) for genre in genres]
    form.publisher.choices = [
        (publisher["name"], publisher["name"]) for publisher in publishers
    ]
    form.tags.choices = [(tag["name"], tag["name"]) for tag in tags]

    if request.method == "POST" and form.validate_on_submit():
        if form.delete.data:
            dao.delete(form.book_id.data)
        else:
            book = Book(
                book_id=form.book_id.data,
                title=form.title.data,
                sub_title=form.sub_title.data,
                summary=form.summary.data,
                publication_year=form.publication_year.data,
                edition=form.edition.data,
                url=form.url.data,
                image=request.form.get("image"),
                created_at=form.created_at.data,
            )
            file = request.files["file"]
            if file and allowed_file(file.filename):
                extension = get_extension(file.filename)
                filename = f"{form.book_id.data}.{extension}"
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            dao.update(
                book,
                form.genre.data,
                form.tags.data,
                form.publisher.data,
                form.authors.data,
            )
        return redirect(url_for("admin.books"))
    return render_template("admin/books/detail.html", form=form, image=image)


@admin_routes.route("/authors", methods=["GET"])
@login_required
def authors():
    dao = AuthorDAO(current_app.driver)
    authors = dao.all()
    return render_template("admin/authors/index.html", authors=authors)


@admin_routes.route("/authors/register", methods=["GET", "POST"])
@login_required
def author_create():
    dao = AuthorDAO(current_app.driver)
    form = AuthorRegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        publishers = dao.register(form.name.data, genrerate_uuid())
        return redirect(url_for("admin.authors"))
    return render_template("admin/authors/register.html", form=form)


@admin_routes.route("/authors/<uuid>/", methods=["GET", "POST"])
@login_required
def author_detail(uuid):
    dao = AuthorDAO(current_app.driver)
    author = dao.find(uuid)
    form = AuthorUpdateForm(name=author["name"], uuid=author["uuid"])
    if request.method == "POST" and form.validate_on_submit():
        if form.delete.data:
            dao.delete(uuid)
        else:
            dao.update(form.name.data, uuid)
        return redirect(url_for("admin.authors"))
    return render_template("admin/authors/detail.html", form=form)


@admin_routes.route("/genres", methods=["GET"])
@login_required
def genres():
    dao = GenreDAO(current_app.driver)
    genres = dao.all()
    return render_template("admin/genres/index.html", genres=genres)


@admin_routes.route("/genre/register", methods=["GET", "POST"])
@login_required
def genre_create():
    dao = GenreDAO(current_app.driver)
    form = GenreRegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        dao.register(form.name.data, form.name_en.data, genrerate_uuid())
        return redirect(url_for("admin.genres"))
    return render_template("admin/genres/register.html", form=form)


@admin_routes.route("/genres/<uuid>/", methods=["GET", "POST"])
@login_required
def genre_detail(uuid):
    dao = GenreDAO(current_app.driver)
    genre = dao.find(uuid)
    form = GenreUpdateForm(
        name=genre["name"], name_en=genre["name_en"], uuid=genre["uuid"]
    )
    if request.method == "POST" and form.validate_on_submit():
        if form.delete.data:
            dao.delete(uuid)
        else:
            dao.update(form.name.data, form.name_en.data, uuid)
        return redirect(url_for("admin.genres"))
    return render_template("admin/genres/detail.html", form=form)


@admin_routes.route("/tags", methods=["GET"])
@login_required
def tags():
    dao = TagDAO(current_app.driver)
    tags = dao.all()
    return render_template("admin/tags/index.html", tags=tags)


@admin_routes.route("/tags/register", methods=["GET", "POST"])
@login_required
def tag_create():
    form = TagRegistrationForm(request.form)
    dao = TagDAO(current_app.driver)
    if request.method == "POST" and form.validate_on_submit():
        dao.register(form.name.data, genrerate_uuid())
        return redirect(url_for("admin.tags"))
    return render_template("admin/tags/register.html", form=form)


@admin_routes.route("/tags/<uuid>/", methods=["GET", "POST"])
@login_required
def tag_detail(uuid):
    dao = TagDAO(current_app.driver)
    tag = dao.find(uuid)
    form = TagUpdateForm(name=tag["name"], uuid=tag["uuid"])
    if request.method == "POST" and form.validate_on_submit():
        if form.delete.data:
            dao.delete(uuid)
        else:
            dao.update(form.name.data, uuid)
        return redirect(url_for("admin.tags"))
    return render_template("admin/tags/detail.html", form=form)


@admin_routes.route("/publishers", methods=["GET"])
@login_required
def publishers():
    dao = PublisherDAO(current_app.driver)
    publishers = dao.all()
    return render_template("admin/publishers/index.html", publishers=publishers)


@admin_routes.route("/publishers/register", methods=["GET", "POST"])
@login_required
def publisher_create():
    form = PublisherRegistrationForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        dao = PublisherDAO(current_app.driver)
        publishers = dao.register(form.name.data, genrerate_uuid())
        return redirect(url_for("admin.publishers"))
    return render_template("admin/publishers/register.html", form=form)


@admin_routes.route("/publishers/<uuid>/", methods=["GET", "POST"])
@login_required
def publisher_detail(uuid):
    dao = PublisherDAO(current_app.driver)
    publisher = dao.find(uuid)
    form = PublisherUpdateForm(name=publisher["name"], uuid=publisher["uuid"])
    if request.method == "POST" and form.validate_on_submit():
        if form.delete.data:
            dao.delete(uuid)
        else:
            dao.update(form.name.data, uuid)
        return redirect(url_for("admin.publisher"))
    return render_template("admin/publishers/detail.html", form=form)
