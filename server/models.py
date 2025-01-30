from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from werkzeug.security import generate_password_hash, check_password_hash
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)
db = SQLAlchemy(metadata=metadata)

# Models go here!
class Game(db.Model):
    __tablename__ = 'games'

    game_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    release_year = db.Column(db.Integer)
    photo_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)

    # Relationships
    player_games = db.relationship('PlayerGame', back_populates='game', cascade='all, delete-orphan')
    category = db.relationship('Category', back_populates='games')

    def __repr__(self):
        return f"<Game(title='{self.title}', genre='{self.genre}', release_year={self.release_year})>"


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)

    # Relationships
    games = db.relationship('Game', back_populates='category', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Category(category_name='{self.category_name}')>"


class Player(db.Model):
    __tablename__ = 'players'

    player_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.country_id'), nullable=False)
    password_hash = db.Column(db.String(128))  # Added password_hash column

    # Relationships
    player_games = db.relationship('PlayerGame', back_populates='player', cascade='all, delete-orphan')
    country = db.relationship('Country', back_populates='players')

    def __repr__(self):
        return f"<Player(username='{self.username}', email='{self.email}')>"

    # Method to set the password (hashes the password)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check if the provided password matches the hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Country(db.Model):
    __tablename__ = 'countries'

    country_id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(30), nullable=False)

    # Relationships
    players = db.relationship('Player', back_populates='country', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Country(country_name='{self.country_name}')>"


class PlayerGame(db.Model):
    __tablename__ = 'player_games'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.player_id'), nullable=False)
    review = db.Column(db.String(255))
    rating=db.Column(db.Float,nullable=True)

    # Relationships
    game = db.relationship('Game', back_populates='player_games')
    player = db.relationship('Player', back_populates='player_games')

    def __repr__(self):
        return f"<PlayerGame(game_id={self.game_id}, player_id={self.player_id}, review='{self.review}')>"