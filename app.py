from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.before_request
    def log_request():
        from flask import request
        print(request.path)

    @app.route("/health")
    def health():
        return "", 200

    return app


if __name__ == "__main__":
    create_app().run()
