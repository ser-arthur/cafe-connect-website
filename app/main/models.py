from app.main import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    map_url = db.Column(db.String(350), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    country = db.Column(db.String(20), nullable=False)
    currency = db.Column(db.String(10), nullable=True)
    coffee_price = db.Column(db.String(10), nullable=False)
    wifi_strength = db.Column(db.Integer, nullable=True)
    seats = db.Column(db.Integer, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    images = db.Column(db.String, nullable=True)
    full_review = db.Column(db.String(300), nullable=True)
    full_rating = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        """Converts the SQLAlchemy model instance into a dictionary."""
        model_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return model_dict


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """Hashes the password and stores the hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the hashed password against the user-provided password."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Converts the SQLAlchemy model instance into a dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }
