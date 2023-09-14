from flask import Flask, render_template


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return render_template("index.html")

    return app
