from flask import Flask, render_template


def create_app() -> Flask:
    app = Flask(__name__, static_url_path="/")

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    return app
