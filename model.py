from uuid import uuid4
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UUIDMixin:
    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

class Actor(UUIDMixin, db.Model):
    __tablename__ = 'actor'
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    films = relationship('FilmActor', back_populates='actor')

    __table_args__ = (
        CheckConstraint('length(first_name) < 20', name='check_length_fname'),
        CheckConstraint('length(last_name) < 25', name='check_length_lname'),
        CheckConstraint('age > 0 and age < 101', name='check_age'),
        UniqueConstraint('first_name', 'last_name', 'age', name='unique_actor')
    )

    def __repr__(self):
        return f'{self.__class__.__name__} fname={self.first_name!r} lname={self.last_name!r} age={self.age!r}'

class Film(UUIDMixin, db.Model):
    __tablename__ = 'film'
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    people = relationship('FilmActor', back_populates='film')

    __table_args__ = (
        CheckConstraint('length(title) < 20', name='check_length_title'),
        CheckConstraint('length(description) < 500', name='check_length_description'),
        CheckConstraint('year < 2030 and year > 1900', name='check_year'),
        UniqueConstraint('title', 'year', name='unique_film')
    )

class FilmActor(UUIDMixin, db.Model):
    __tablename__ = 'film_actor'
    film_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey('film.id'), nullable=False)
    actor_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey('actor.id'), nullable=False)

    film = relationship('Film', back_populates='people')
    actor = relationship('Actor', back_populates='films')

    __table_args__ = (
        UniqueConstraint('film_id', 'actor_id', name='film_actor_combines_unique'),
    )
