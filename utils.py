"""This module provides utility functions."""
import os

import requests
from dotenv import load_dotenv

import config

load_dotenv()

OK = 200


def get_db_url() -> str:
    """
    Construct the database URL from environment variables.

    The required environment variables are:
    - HOST: The database host.
    - PORT: The database port.
    - USER: The database user.
    - PASS: The database user's password.
    - DB_NAME: The database name.

    Returns:
        str: The constructed database URL in the format required by SQLAlchemy.
    """
    postgres_values = 'HOST', 'PORT', 'USER', 'PASS', 'DB_NAME'
    credentials = {varible: os.environ.get(varible) for varible in postgres_values}
    return 'postgresql+psycopg://{USER}:{PASS}@{HOST}:{PORT}/{DB_NAME}'.format(**credentials)


def get_rating_movie(title):
    """
    Fetch movie rating data from an external API based on the movie title.

    Args:
        title (str): The title of the movie to search for.

    Returns:
        dict: A dictionary containing movie data if the request is successful.
        None: If the request is unsuccessful, None is returned and an error message is printed.
    """
    headers = {
        'accept': 'application/json',
        'X-API-KEY': config.API_KEY,
    }
    response = requests.get(config.API_URL + title, headers=headers)
    if response.status_code == OK:
        return response.json()
