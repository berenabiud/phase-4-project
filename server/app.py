#!/usr/bin/env python3
from models import db, Game,Player,PlayerGame
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Hi Welcome</h1>"
class GameResource(Resource):
    def get(self, game_id=None):
        """Retrieve a specific game by its ID or all games."""
        if game_id:
            # Retrieve a single game by ID
            game = Game.query.get(game_id)
            if game:
                return jsonify({
                    'game_id': game.game_id,
                    'title': game.title,
                    'release_year': game.release_year,
                    'photo_url': game.photo_url,
                    'category': game.category.category_name
                })
            return jsonify({'message': 'Game not found'}), 404
        else:
            # Retrieve all games if no game_id is provided
            games = Game.query.all()
            return jsonify([{
                'game_id': game.game_id,
                'title': game.title,
                'release_year': game.release_year,
                'photo_url': game.photo_url,
                'category': game.category.category_name
            } for game in games])

    def post(self):
        """Create a new game."""
        data = request.get_json()
        new_game = Game(
            title=data['title'],
            release_year=data.get('release_year'),
            photo_url=data.get('photo_url'),
            category_id=data['category_id']
        )
        db.session.add(new_game)
        db.session.commit()
        return jsonify({'message': 'Game added successfully!', 'game_id': new_game.game_id})

    def patch(self, game_id):
        """Update an existing game partially."""
        data = request.get_json()
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'message': 'Game not found'}), 404
        
        # Update the game properties that were passed
        if 'title' in data:
            game.title = data['title']
        if 'release_year' in data:
            game.release_year = data['release_year']
        if 'photo_url' in data:
            game.photo_url = data['photo_url']
        if 'category_id' in data:
            game.category_id = data['category_id']
        
        db.session.commit()
        return jsonify({'message': 'Game updated successfully!'})

# Define routes for GameResource
api.add_resource(GameResource, '/games', '/games/<int:game_id>')
