from __future__ import annotations
from typing import Type

from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    
    from .models import User

    with app.app_context():
        db.create_all()
        create_admin()

    return app

def create_admin():
    from .models import User  # import here to avoid circular issues

    admin_email = "mizbahkounain@gmail.com"

    existing = User.query.filter_by(email=admin_email).first()

    if not existing:
        admin = User(
            email=admin_email,
            status="ACTIVE",
            role="ADMIN"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created!")
