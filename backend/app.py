"""
Flask application factory.
"""
from flask import Flask
from flask_cors import CORS
from flask_caching import Cache

cache = Cache()


def create_app() -> Flask:
    app = Flask(__name__)

    from config import config
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["CACHE_TYPE"] = config.CACHE_TYPE
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)

    from routes.sentiment import sentiment_bp
    from routes.price import price_bp

    app.register_blueprint(sentiment_bp, url_prefix="/api")
    app.register_blueprint(price_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
