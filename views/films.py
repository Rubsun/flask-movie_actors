"""
This module defines routes and functions for managing films in a Flask web application.

It includes routes for listing films, viewing film details, adding films, updating films,
and deleting films.
"""


from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import Integer, cast, delete, select, update
from werkzeug.exceptions import Conflict, NotFound

from model import Actor, Film, FilmActor, db
from utils import get_rating_movie

films_app = Blueprint('films_app', __name__)

GET = 'GET'


@films_app.get('/', endpoint='list')
def get_films():
    """
    Retrieve a list of films from the database and render them on the films index page.

    Returns:
        str: Rendered HTML template displaying a list of films.
    """
    films = db.session.scalars(select(Film))
    return render_template('films/index.html', films=films)


@films_app.get('/detail', endpoint='detail')
def detail():
    """
    Display detailed information about a specific film based on the provided title and year.

    Retrieves film details from the database and renders them along with associated actors on
    the 'films/detail.html' template.

    Returns:
        str: Rendered HTML template displaying film details and associated actors.

    Raises:
        NotFound: If the film with the specified title and year is not found in the database.
    """
    title = request.args.get('title')
    year = request.args.get('year', type=int)
    film = db.session.scalar(
        select(Film).where(Film.title == title, Film.year == year),
    )
    if not film:
        raise NotFound(f'Film with title: {title} not found!!!')

    movie_data = get_rating_movie(title)
    actors = [film_actor.actor for film_actor in film.people]
    return render_template('films/detail.html', film=film, actors=actors, movie_data=movie_data)


@films_app.route('/add/', methods=[GET, 'POST'], endpoint='add')
def add_film():
    """
    Add a new film to the database.

    If the request method is GET, renders the 'films/add.html' template to display a form
    for adding a new film. If the method is POST, processes the form data to create a new film
    and associate it with an existing actor in the database.

    Returns:
        redirect: Redirects to the 'films_app.detail' endpoint to display the added film details.

    Raises:
        NotFound: If the specified actor is not found in the database.
        Conflict: If the allready exists.
    """
    if request.method == GET:
        return render_template('films/add.html')

    first_name = request.form['actor-first-name']
    last_name = request.form['actor-last-name']
    age = request.form['actor-age']
    title = request.form['film-title']
    description = request.form['film-description']
    year = request.form['film-year']

    actor = db.session.scalar(
        select(Actor).where(
            Actor.first_name == first_name,
            Actor.last_name == last_name,
            Actor.age == cast(age, Integer),
        ),
    )
    if not actor:
        raise NotFound(f'Actor with name "{first_name}" not found')

    films = [film_actor.film for film_actor in actor.films]
    titles = [film.title for film in films]
    if title in titles:
        raise Conflict(
            f'This actor has already a film "{title}" in {year}!',
        )

    film = db.session.scalar(
        select(Film).where(
            Film.title == title,
            Film.year == cast(year, Integer),
        ),
    )

    if not film:
        film = Film(title=title, description=description, year=year)
        db.session.add(film)
        db.session.commit()

    film_actor = FilmActor(actor_id=actor.id, film_id=film.id)
    db.session.add(film_actor)
    db.session.commit()

    return redirect(
        url_for(
            'films_app.detail', title=title, year=year,
        ),
    )


@films_app.route('/update/<uuid:film_id>', methods=['GET', 'POST'], endpoint='update')
def update_film(film_id):
    """
    Update information for an existing film in the database.

    If the request method is GET, renders the 'films/update.html' template to display a form
    for updating film details. If the method is POST, processes the form data to update the
    specified film's information in the database.

    Args:
        film_id (UUID): The ID of the film to update.

    Returns:
        redirect: Redirects to the film detail page for the updated film.

    Raises:
        NotFound: If the film with the id
        Conflict: If the new film information conflicts with an existing film in the database.
    """
    film = db.session.get(Film, film_id)
    if not film:
        raise NotFound(f'Film with id "{film_id}" not found!')

    if request.method == GET:
        return render_template('films/update.html', film=film)

    title = request.form['new-film-title']
    description = request.form['new-film-description']
    year = request.form['new-film-year']

    existing_new_film = db.session.scalar(
        select(Film).where(
            Film.title == title,
            Film.year == cast(year, Integer),
        ),
    )
    if existing_new_film:
        raise Conflict(
            f'Film with title: "{title}" with {year} already exists!',
        )

    db.session.execute(
        update(Film).where(Film.id == film_id).values
        (
            title=title,
            description=description,
            year=year,
        ),
    )
    db.session.commit()

    return redirect(
        url_for(
            'films_app.detail', title=title, year=year,
        ),
    )


@films_app.route('/delete/<uuid:film_id>', methods=[GET, 'POST'], endpoint='delete')
def delete_film(film_id):
    """
    Delete a film from the database by id.

    Args:
        film_id (UUID): The id of the film to delete.

    Returns:
        redirect: Redirects to the film list page for the deleted film.

    Raises:
        NotFound: If the film with the id
    """
    film = db.session.get(Film, film_id)
    if not film:
        raise NotFound(f'Film with id "{film_id}" not found!')

    db.session.execute(
        delete(FilmActor).where(FilmActor.film_id == film.id),
    )
    db.session.delete(film)
    db.session.commit()

    return redirect(url_for('films_app.list'))


@films_app.post('/delete/<uuid:film_id>/<uuid:actor_id>', endpoint='delete_film_by_actor')
def delete_film_by_actor(film_id, actor_id):
    """
    Delete a film from a specific actor.

    Args:
        film_id (UUID): The ID of the film to be deleted.
        actor_id (UUID): The ID of the actor whose film is to be deleted.

    Returns:
        redirect: Redirects to the actor detail page after successful deletion.

    Raises:
        NotFound: If the specified actor or film is not found.
    """
    actor = db.session.get(Actor, actor_id)
    if not actor:
        raise NotFound(f'Actor with id "{actor_id}" not found!')

    film_actor = db.session.scalar(
        select(FilmActor).where(FilmActor.film_id == film_id, FilmActor.actor_id == actor_id),
    )
    if not film_actor:
        raise NotFound(f'Film with id "{film_id}" not found for actor with id "{actor_id}"!')

    db.session.delete(film_actor)
    db.session.commit()

    return redirect(
        url_for(
            'actors_app.detail',
            first_name=actor.first_name,
            last_name=actor.last_name,
            age=actor.age,
        ),
    )
