"""Initial migration.

Revision ID: 2b2ff8004ff5
Revises: 
Create Date: 2024-05-30 19:45:00.907436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b2ff8004ff5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('actor',
    sa.Column('first_name', sa.String(length=20), nullable=False),
    sa.Column('last_name', sa.String(length=25), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.CheckConstraint('age > 0 and age < 101', name='check_age'),
    sa.CheckConstraint('length(first_name) < 20', name='check_length_fname'),
    sa.CheckConstraint('length(last_name) < 25', name='check_length_lname'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('first_name', 'last_name', 'age', name='unique_actor')
    )
    op.create_table('film',
    sa.Column('title', sa.String(length=20), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.CheckConstraint('length(description) < 500', name='check_length_description'),
    sa.CheckConstraint('length(title) < 20', name='check_length_title'),
    sa.CheckConstraint('year < 2030 and year > 1900', name='check_year'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title', 'year', name='unique_film')
    )
    op.create_table('film_actor',
    sa.Column('film_id', sa.UUID(), nullable=False),
    sa.Column('actor_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['actor_id'], ['actor.id'], ),
    sa.ForeignKeyConstraint(['film_id'], ['film.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('film_id', 'actor_id', name='film_actor_combines_unique')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('film_actor')
    op.drop_table('film')
    op.drop_table('actor')
    # ### end Alembic commands ###
