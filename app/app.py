import os
from flask import Flask
from config import Config
from extensions import db, jwt
from app.routes import routes
from flask_migrate import Migrate
from models import Patient, Visit


def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
    app.config.from_object(Config)
    migrate = Migrate(app, db)
    db.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(routes)
    

    with app.app_context():
        db.create_all()
    from models import Patient  # ⬅️ Очень важно для миграций

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
