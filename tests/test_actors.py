"""Unit tests for actor-related operations in the Flask application."""
import unittest
from uuid import uuid4

from app import create_app, db
from model import Actor


class ActorsTestCase(unittest.TestCase):
    """Test case for actor-related operations in the Flask application."""

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

    def test_detail_missing_parameters(self):
        """Test retrieving actor details with missing parameters."""
        response = self.client.get('/actors/actor')
        self.assertEqual(response.status_code, 400)

    def test_get_add_actor_form(self):
        """Test retrieving the form to add a new actor."""
        response = self.client.get('/actors/add/')
        self.assertIn(b'Add Actor', response.data)

    def test_add_actor(self):
        """Test adding a new actor."""
        response = self.client.post('/actors/add/', data={
            'actor-first-name': 'John',
            'actor-last-name': 'Doe',
            'actor-age': '30',
        })
        self.assertEqual(response.status_code, 302)

    def test_detail_actor_not_found(self):
        """Test retrieving details of an actor that does not exist."""
        actor = Actor(first_name='Mike', last_name='Jones', age=40)
        db.session.add(actor)
        db.session.commit()
        response = self.client.get('/actors/actor?first_name=John&last_name=NoDoes&age=30')
        self.assertEqual(response.status_code, 404)

    def test_detail_success(self):
        """Test retrieving details of an existing actor."""
        actor = Actor(first_name='Mike', last_name='Jones', age=40)
        db.session.add(actor)
        db.session.commit()
        response = self.client.get('/actors/actor?first_name=Mike&last_name=Jones&age=40')
        self.assertEqual(response.status_code, 200)

    def test_get_update(self):
        """Test retrieving the form to update an actor."""
        actor = Actor(first_name='John', last_name='Doe', age=30)
        db.session.add(actor)
        db.session.commit()
        response = self.client.get(f'/actors/update/{actor.id}')
        self.assertIn(b'Update Actor', response.data)

    def test_update_not_found(self):
        """Test updating an actor that does not exist."""
        response = self.client.post(f'/actors/update/{uuid4()}', data={
            'actor-new-first-name': 'NoJohn',
            'new-actor-last-name': 'Doe',
            'new-actor-age': '30',
        })
        self.assertEqual(response.status_code, 404)

    def test_update_conflict(self):
        """Test updating an actor with conflicting information."""
        actor = Actor(first_name='John', last_name='Doe', age=30)
        db.session.add(actor)
        db.session.commit()
        response = self.client.post(f'/actors/update/{actor.id}', data={
            'actor-new-first-name': 'John',
            'new-actor-last-name': 'Doe',
            'new-actor-age': '30',
        })
        self.assertEqual(response.status_code, 409)

    def test_update_success(self):
        """Test updating an existing actor successfully."""
        actor = Actor(first_name='John', last_name='Doe', age=30)
        db.session.add(actor)
        db.session.commit()
        response = self.client.post(f'/actors/update/{actor.id}', data={
            'actor-new-first-name': 'NewJohn',
            'new-actor-last-name': 'NewDoe',
            'new-actor-age': '35',
        })
        self.assertEqual(response.status_code, 302)

    def test_delete_get_form(self):
        """Test retrieving the form to delete an actor."""
        actor = Actor(first_name='John', last_name='Doe', age=30)
        db.session.add(actor)
        db.session.commit()
        response = self.client.get(f'/actors/delete/{actor.id}')
        self.assertEqual(response.status_code, 302)

    def test_delete_success(self):
        """Test deleting an existing actor successfully."""
        actor = Actor(first_name='John', last_name='Doe', age=30)
        db.session.add(actor)
        db.session.commit()
        response = self.client.post(f'/actors/delete/{actor.id}')
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(db.session.get(Actor, actor.id))


if __name__ == '__main__':
    unittest.main()
