"""
Module for handling actor and film-related operations using Flask and SQLAlchemy.

This module defines routes and functions within Flask Blueprints for managing actors and films
in a database. It includes functionality for adding, updating, deleting, and displaying details
of actors and films.
"""

from flask import Blueprint, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import Integer, cast, delete, select, update
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from model import Actor, FilmActor, db

actors_app = Blueprint('actors_app', __name__)
csrf = CSRFProtect()

GET = 'GET'


@actors_app.get('/', endpoint='list')
def get_actors():
    """
    Retrieve a list of actors from the database and render them on the actors index page.

    Returns:
        str: Rendered HTML template displaying a list of actors.
    """
    actors = db.session.scalars(select(Actor))
    return render_template('actors/index.html', actors=actors)


@actors_app.get('/actor', endpoint='detail')
def detail():
    """
    Display detailed information about a specific actor based on the provided parameters.

    Retrieves actor details from the database based on the provided first name, last name, and age
    parameters. If any of these parameters are missing, it returns a 400 error with a message.
    If the actor is not found in the database, it raises a NotFound error.

    Returns:
        str: Rendered HTML template displaying actor details and associated films.

    Raises:
        NotFound: If the actor with the specified name and age is not found in the database.
    """
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    age = request.args.get('age', type=int)
    if not first_name or not last_name or not age:
        return BadRequest('Missing required parameters')

    actor = db.session.scalar(
        select(Actor).where(
            Actor.first_name == first_name,
            Actor.last_name == last_name,
            Actor.age == age,
        ),
    )

    if not actor:
        raise NotFound(f'Actor with name "{first_name}" not found!')

    films = [film_actor.film for film_actor in actor.films]

    return render_template(
        'actors/detail.html', first_name=first_name, actor=actor, films=films,
    )


@actors_app.route('/add/', methods=[GET, 'POST'], endpoint='add')
def add_actor():
    """
    Add a new actor to the database.

    If the request method is GET, renders the 'actors/add.html' template to display a form
    for adding a new actor. If the method is POST, processes the form data to create a new
    actor in the database.

    Returns:
        redirect: Redirects to the actor detail page for the added actor.
    """
    if request.method == GET:
        return render_template('actors/add.html')

    first_name = request.form['actor-first-name']
    last_name = request.form['actor-last-name']
    age = request.form['actor-age']

    actor = db.session.scalar(
        select(Actor).where(
            Actor.first_name == first_name,
            Actor.last_name == last_name,
            Actor.age == cast(age, Integer),
        ),
    )
    if not actor:
        actor = Actor(first_name=first_name, last_name=last_name, age=age)
        db.session.add(actor)
        db.session.commit()
    return redirect(
        url_for(
            'actors_app.detail', first_name=first_name, last_name=last_name, age=age,
        ),
    )


@actors_app.route('/update/<uuid:actor_id>', methods=['GET', 'POST'], endpoint='update')
def update_actor(actor_id):
    """
    Update information for an existing actor in the database.

    If the request method is GET, renders the 'actors/update.html' template to display a form
    for updating actor details. If the method is POST, processes the form data to update the
    specified actor's information in the database.

    Args:
        actor_id (UUID): The ID of the actor to update.

    Returns:
        redirect: Redirects to the actor detail page for the updated actor.

    Raises:
        NotFound: If the specified actor with the old details is not found in the database.
        Conflict: If the new actor information conflicts with an existing actor in the database.
    """
    actor = db.session.get(Actor, actor_id)
    if not actor:
        raise NotFound(f'Actor with id "{actor_id}" not found!')

    if request.method == GET:
        return render_template('actors/update.html', actor=actor)

    first_name = request.form['actor-new-first-name']
    last_name = request.form['new-actor-last-name']
    new_age = request.form['new-actor-age']

    existing_new_actor = db.session.scalar(
        select(Actor).where(
            Actor.first_name == first_name,
            Actor.last_name == last_name,
            Actor.age == cast(new_age, Integer),
        ),
    )
    if existing_new_actor:
        raise Conflict(
            f'Actor "{first_name} {last_name}" with age {new_age} already exists!',
        )

    url_detail = url_for(
        'actors_app.detail', first_name=first_name, last_name=last_name, age=new_age,
    )

    db.session.execute(
        update(Actor).where(Actor.id == actor_id).values
        (
            first_name=first_name,
            last_name=last_name,
            age=new_age,
        ),
    )
    db.session.commit()
    return redirect(url_detail)


@actors_app.route('/delete/<uuid:actor_id>', methods=[GET, 'POST'], endpoint='delete')
@csrf.exempt
def delete_actor(actor_id):
    """
    Delete an existing actor from the database along with associated films.

    If the request method is GET, renders the 'actors/delete.html' template to display a form
    for confirming the deletion of an actor. If the method is POST, processes the form data to
    delete the specified actor from the database and any associated films if they have no other
    related actors.

    Args:
        actor_id (UUID): The ID of the actor to delete.

    Returns:
        redirect: Redirects to the actors list page after successful deletion.

    Raises:
        NotFound: If the specified actor is not found in the database.
    """
    actor = db.session.get(Actor, actor_id)
    if not actor:
        raise NotFound(f'Actor with id "{actor_id}" not found!')

    films_to_delete = []

    for film_actor in actor.films:
        film = film_actor.film
        if len(film.people) == 1:
            films_to_delete.append(film)
    db.session.execute(
        delete(FilmActor).where(FilmActor.actor_id == actor.id),
    )

    for film_to_delete in films_to_delete:
        db.session.delete(film_to_delete)

    db.session.delete(actor)

    db.session.commit()
    return redirect(url_for('actors_app.list'))
