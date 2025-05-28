from flask import Flask
from app.extensions import db, jwt
import os


def create_app():
    # ⬅️ Указан путь к шаблонам (как у вас сейчас)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_path = os.path.abspath(os.path.join(base_dir, "..", "templates"))
    app = Flask(__name__, template_folder=template_path)

    # 🔧 Конфигурация
    app.config["SECRET_KEY"] = "your-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(base_dir, '../instance/users.db')}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 🔐 JWT настройки
    app.config["JWT_SECRET_KEY"] = "your-jwt-secret-key"
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # 🔌 Инициализация расширений
    db.init_app(app)
    jwt.init_app(app)

    # 🔁 Импорт роутов
    from app.routes import routes
    app.register_blueprint(routes)

    return app
