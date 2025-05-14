from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Расширения
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # 🔧 Настройки безопасности и JWT
    app.config["SECRET_KEY"] = "your-secret-key"  # Замени на безопасный ключ
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/users.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 🔐 JWT настройки (без CSRF)
    app.config["JWT_SECRET_KEY"] = "your-jwt-secret-key"  # Замени на безопасный ключ
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = False  # True для HTTPS
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # ⬅️ Отключена защита CSRF

    # Инициализация
    db.init_app(app)
    jwt.init_app(app)

    # Импорт роутов
    from app.routes import routes
    app.register_blueprint(routes)

    return app
