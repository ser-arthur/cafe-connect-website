import os

class Config:
    # Secret key for CSRF protection and session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'it-is-what-it-is'
    API_KEY = os.environ.get('API_KEY') or 'guess-it-right'

    # Database URI for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///cc-database.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
