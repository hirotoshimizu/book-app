from flask import Blueprint, render_template

graph_routes = Blueprint("graphs", __name__, url_prefix="/graphs")


@graph_routes.get("/")
def get_graphs():
    return render_template("graphs.html")
