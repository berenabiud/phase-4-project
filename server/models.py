from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(metadata=metadata)

# Models go here!
class Game(db.Model):
    __tablename__ = 'games'

    game_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # Name of the game
    genre = db.Column(db.String(50), nullable=False)   # Genre (e.g., RPG, Action)
    release_year = db.Column(db.Integer)              # Year the game was released
    photo_url = db.Column(db.String(255))             # URL or path to the game's photo

    player_games = db.relationship('PlayerGame', back_populates='game', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Game(title='{self.title}', genre='{self.genre}', release_year={self.release_year}, photo_url='{self.photo_url}')>"



class Player(db.Model):
    __tablename__ = 'players'

    player_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)  # Player's username
    email = db.Column(db.String(120), nullable=False, unique=True)    # Player's email

    # One-to-Many relationship with PlayerGame
    player_games = db.relationship('PlayerGame', back_populates='player', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Player(username='{self.username}', email='{self.email}')>"


class PlayerGame(db.Model):
    __tablename__ = 'player_games'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)  # Foreign key to Game
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)  # Foreign key to Player
    review = db.Column(db.String(255))  # User-submittable attribute (e.g., review of the game)

    # Relationships
    game = db.relationship('Game', back_populates='player_games')
    player = db.relationship('Player', back_populates='player_games')

    def __repr__(self):
        return f"<PlayerGame(game_id={self.game_id}, player_id={self.player_id}, review='{self.review}')>"

