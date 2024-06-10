"""Unit tests for film-related operations in the Flask application."""

import unittest
from uuid import uuid4

from app import create_app, db
from model import Actor, Film, FilmActor


class FilmsTestCase(unittest.TestCase):
    """Test case for film-related operations in the Flask application."""

    def setUp(self):
        """Set up the test environment."""
        self.app = create_app('config.TestConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        """Tear down the test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_films(self):
        """Test retrieving the list of films."""
        response = self.client.get('/films/')
        self.assertEqual(response.status_code, 200)

    def test_add_film(self):
        """Test adding a new film."""
        actor = Actor(first_name='Tom', last_name='Hanks', age=60)
        db.session.add(actor)
        db.session.commit()

        response = self.client.post('/films/add/', data={
            'actor-first-name': 'Tom',
            'actor-last-name': 'Hanks',
            'actor-age': 60,
            'film-title': 'Forrest Gump',
            'film-description': 'A story about a man named Forrest.',
            'film-year': 1994,
        })
        self.assertEqual(response.status_code, 302)  # Redirect after adding film

        film = db.session.query(Film).filter_by(
            title='Forrest Gump', year=1994,
        ).one_or_none()
        self.assertIsNotNone(film)

    def test_update_film(self):
        """Test updating an existing film."""
        film = Film(title='Big', description='A story about a boy who becomes an adult overnight.', year=1988)
        db.session.add(film)
        db.session.commit()

        response = self.client.post(f'/films/update/{film.id}', data={
            'new-film-title': 'B3ig',
            'new-film-description': 'A story qweabout a boy who magically becomes an adult.',
            'new-film-year': 1978,
        })
        self.assertEqual(response.status_code, 302)

        updated_film = db.session.query(Film).filter_by(
            title='B3ig', description='A story qweabout a boy who magically becomes an adult.', year=1978,
        ).one_or_none()
        self.assertIsNotNone(updated_film)

    def test_delete_film(self):
        """Test deleting an existing film."""
        film = Film(title='Cast Away', description='A man stranded on an island.', year=2000)
        db.session.add(film)
        db.session.commit()

        response = self.client.post(f'/films/delete/{film.id}')
        self.assertEqual(response.status_code, 302)

        deleted_film = db.session.query(Film).filter_by(
            title='Cast Away', description='A man stranded on an island.', year=2000,
        ).one_or_none()
        self.assertIsNone(deleted_film)

    def test_delete_film_by_actor(self):
        """Test deleting a film from a specific actor."""
        actor = Actor(first_name='Tom', last_name='Hanks', age=60)
        film = Film(title='Forrest Gump', description='A story about a man named Forrest.', year=1994)
        db.session.add(actor)
        db.session.add(film)
        db.session.commit()

        film_actor = FilmActor(actor_id=actor.id, film_id=film.id)
        db.session.add(film_actor)
        db.session.commit()

        response = self.client.post(f'/films/delete/{film.id}/{actor.id}')
        self.assertEqual(response.status_code, 302)

        film_actor = db.session.query(FilmActor).filter_by(
            actor_id=actor.id, film_id=film.id,
        ).one_or_none()
        self.assertIsNone(film_actor)


if __name__ == '__main__':
    unittest.main()
