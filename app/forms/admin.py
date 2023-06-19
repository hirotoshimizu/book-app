import datetime

from flask import Blueprint, current_app
from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
    ValidationError,
    validators,
)

from app.dao.author import AuthorDAO
from app.dao.books import BookDAO
from app.dao.genres import GenreDAO
from app.dao.publisher import PublisherDAO
from app.dao.tag import TagDAO

forms_routes = Blueprint("forms", __name__, None)


def get_current_year():
    date = datetime.date.today()
    year = int(date.strftime("%Y"))
    return int(date.year)


class LoginForm(FlaskForm):
    email = StringField("Email")
    password = PasswordField("Password")
    submit = SubmitField("Sign in")

    def validate_email(self, email):
        if email.data == "":
            raise ValidationError("Emailを入力してください。")

    def validate_password(self, password):
        if password.data == "":
            raise ValidationError("パスワードを入力してください。")


class AuthorRegistrationForm(FlaskForm):
    name = StringField("name", [validators.Length(min=2, max=25)])
    submit = SubmitField("作成")

    def validate_name(self, name):
        dao = AuthorDAO(current_app.driver)
        if name.data == "":
            raise ValidationError("名前を入力してください。")

        if name.data and dao.find_by_name(name.data):
            raise ValidationError("すでに登録済みの名前です。")


class AuthorUpdateForm(FlaskForm):
    uuid = StringField("uuid", render_kw={"readonly": True})
    name = StringField("name", [validators.Length(min=2, max=25)])
    submit = SubmitField("更新")
    delete = SubmitField("削除")

    def validate_name(self, name):
        dao = AuthorDAO(current_app.driver)
        if name.data == "":
            raise ValidationError("名前を入力してください。")

        if name.data and dao.find_by_name(name.data):
            raise ValidationError("すでに登録済みの名前です。")


class BookRegistrationForm(FlaskForm):
    book_id = StringField("book id", [validators.Length(min=2, max=25)])
    title = StringField("title", [validators.Length(min=2, max=25)])
    sub_title = StringField("sub title", [validators.Length(min=2, max=25)])
    authors = SelectMultipleField("authors")
    genre = SelectField("genre")
    publisher = SelectField("publisher")
    tags = SelectMultipleField("tags")
    summary = TextAreaField(
        "summary", [validators.optional(), validators.length(max=1000)]
    )
    edition = SelectField("edition", choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    curret_year = get_current_year()
    publication_year = SelectField(
        "publication year",
        choices=[(i, i) for i in range(curret_year, 1949, -1)],
    )
    url = StringField("url", [validators.Length(min=2, max=50)])
    submit = SubmitField("作成")

    def validate_book_id(self, book_id):
        dao = BookDAO(current_app.driver)
        if book_id.data == "":
            raise ValidationError("book idを入力してください。")

        if book_id.data and dao.detail(book_id.data):
            raise ValidationError("すでに登録済みのbook idです。")

    def validate_name(self, name):
        if name.data == "":
            raise ValidationError("名前を入力してください。")

    def validate_authors(self, authors):
        if not authors.data:
            raise ValidationError("著者を選択してください。")

    def validate_tags(self, tags):
        if not tags.data:
            raise ValidationError("タグを選択してください。")


class BookUpdateForm(FlaskForm):
    book_id = StringField("book id", render_kw={"readonly": True})
    title = StringField("title", [validators.Length(min=2, max=25)])
    sub_title = StringField("sub title", [validators.Length(min=2, max=25)])
    authors = SelectMultipleField("authors")
    genre = SelectField("genre")
    publisher = SelectField("publisher")
    tags = SelectMultipleField("tags")
    summary = TextAreaField(
        "summary", [validators.optional(), validators.length(max=1000)]
    )
    edition = SelectField("edition", choices=[(i, i) for i in range(1, 6)])
    curret_year = get_current_year()
    publication_year = SelectField(
        "publication year",
        choices=[(i, i) for i in range(curret_year, 1949, -1)],
    )
    url = StringField("url", [validators.Length(min=2, max=50)])
    created_at = HiddenField("created_at")
    submit = SubmitField("更新")
    delete = SubmitField("削除")

    def validate_book_id(self, book_id):
        if book_id.data == "":
            raise ValidationError("book idを入力してください。")

    def validate_name(self, name):
        if name.data == "":
            raise ValidationError("名前を入力してください。")

    def validate_authors(self, authors):
        if not authors.data:
            raise ValidationError("著者を選択してください。")

    def validate_tags(self, tags):
        if not tags.data:
            raise ValidationError("タグを選択してください。")


class GenreRegistrationForm(FlaskForm):
    name = StringField("name", [validators.Length(min=2, max=25)])
    name_en = StringField("name en", [validators.Length(min=2, max=25)])
    submit = SubmitField("作成")

    def validate_name(self, name):
        dao = GenreDAO(current_app.driver)
        if name.data == "":
            raise ValidationError("名前を入力してください。")

        if name.data and dao.find_by_name(name.data):
            raise ValidationError("すでに登録済みの名前です。")

    def validate_name_en(self, name_en):
        dao = GenreDAO(current_app.driver)
        if name_en.data == "":
            raise ValidationError("英語名を入力してください。")

        if name_en.data and dao.find_by_name_en(name_en.data):
            raise ValidationError("すでに登録済みの英語名です。")


class GenreUpdateForm(FlaskForm):
    uuid = StringField("uuid", render_kw={"readonly": True})
    name = StringField("name", [validators.Length(min=2, max=25)])
    name_en = StringField("name en", [validators.Length(min=2, max=25)])
    submit = SubmitField("更新")
    delete = SubmitField("削除")

    def validate_name(self, name):
        dao = GenreDAO(current_app.driver)
        if name.data == "":
            raise ValidationError("名前を入力してください。")

        if name.data and dao.find_by_name(name.data):
            raise ValidationError("すでに登録済みの名前です。")

    def validate_name_en(self, name_en):
        dao = GenreDAO(current_app.driver)
        if name_en.data == "":
            raise ValidationError("英語名を入力してください。")

        if name_en.data and dao.find_by_name_en(name_en.data):
            raise ValidationError("すでに登録済みの英語名です。")


class PublisherRegistrationForm(FlaskForm):
    name = StringField("name", [validators.Length(min=2, max=25)])
    submit = SubmitField("作成")

    def validate_name(self, name):
        dao = PublisherDAO(current_app.driver)
        if name.data == "":
            raise ValidationError("名前を入力してください。")

        if name.data and dao.find_by_name(name.data):
            raise ValidationError("すでに登録済みの名前です。")


class PublisherUpdateForm(FlaskForm):
    uuid = StringField("uuid", render_kw={"readonly": True})
    name = StringField("name", [validators.Length(min=2, max=25)])
    submit = SubmitField("更新")
    delete = SubmitField("削除")

    def validate_name(self, name):
        dao = PublisherDAO(current_app.driver)
        if name.data == "":
            raise ValidationError("名前を入力してください。")

        if name.data and dao.find_by_name(name.data):
            raise ValidationError("すでに登録済みの名前です。")


class TagRegistrationForm(FlaskForm):
    name = StringField("name", [validators.Length(min=2, max=25)])
    submit = SubmitField("作成")

    def validate_name(self, name):
        dao = TagDAO(current_app.driver)
        if name.data == "":
            raise ValidationError("名前を入力してください。")

        if name.data and dao.find_by_name(name.data):
            raise ValidationError("すでに登録済みの名前です。")


class TagUpdateForm(FlaskForm):
    uuid = StringField("uuid", render_kw={"readonly": True})
    name = StringField("name", [validators.Length(min=2, max=25)])
    submit = SubmitField("更新")
    delete = SubmitField("削除")

    def validate_name(self, name):
        dao = TagDAO(current_app.driver)
        if name.data == "":
            raise ValidationError("名前を入力してください。")

        if name.data and dao.find_by_name(name.data):
            raise ValidationError("すでに登録済みの名前です。")
