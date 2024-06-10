"""
Movie Database Application.

This module sets up a Flask application for managing actors and films in a database.
It configures the application, initializes the database, and registers blueprints
for actor and film-related operations.
"""
API_KEY = '0E04D5Z-VMVM55X-GRRS461-5MHNK6R'
API_URL = 'https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=1&query='


class Config:
    """
    Base configuration class.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): Database URI for the application.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag to disable modification tracking.
    """

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://hw_rpm:test@localhost:5555/hw_rpm'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """
    Testing configuration class.

    Attributes:
        TESTING (bool): Flag to enable testing mode.
        SQLALCHEMY_DATABASE_URI (str): In-memory SQLite database URI for testing.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
