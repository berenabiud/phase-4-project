#!/usr/bin/env python3
from models import db, Game,Player,PlayerGame,Category
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Hi Welcome</h1>"
from flask import jsonify, request
from flask_restful import Resource
from models import Game, Category, db

from flask import jsonify, request
from flask_restful import Resource
from app import db
from models import Game, Category  # assuming these are your models

class GameResource(Resource):
   from flask import jsonify

class GameResource(Resource):
    def get(self, game_id=None):
        """Retrieve a specific game by its ID or all games."""
        try:
            if game_id:
                # Retrieve a single game by ID
                game = Game.query.get(game_id)
                if game:
                    return jsonify({
                        'game_id': game.game_id,
                        'title': game.title,
                        'release_year': game.release_year,
                        'photo_url': game.photo_url,
                        'category': game.category.category_name if game.category else None
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
                    'category': game.category.category_name if game.category else None
                } for game in games])
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    def post(self):
        """Create a new game."""
        data = request.get_json()

        # Ensure required data is provided
        if 'title' not in data or 'category_id' not in data:
            return jsonify({'message': 'Title and category_id are required'}), 400

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

    def delete(self, game_id):
        """Delete an existing game."""
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'message': 'Game not found'}), 404

        db.session.delete(game)
        db.session.commit()
        return jsonify({'message': 'Game deleted successfully!'})

# Define routes for GameResource
api.add_resource(GameResource, '/games', '/games/<int:game_id>')

class CategoryResource(Resource):
    def get(self, category_id=None):
        """Retrieve a specific category by its ID or all categories."""
        if category_id:
            # Retrieve a single category by ID
            category = Category.query.get(category_id)
            if category:
                return jsonify({
                    'category_id': category.category_id,
                    'category_name': category.category_name
                })
            return jsonify({'message': 'Category not found'}), 404
        else:
            # Retrieve all categories if no category_id is provided
            categories = Category.query.all()
            return jsonify([{
                'category_id': category.category_id,
                'category_name': category.category_name
            } for category in categories])

    def post(self):
        """Create a new category."""
        data = request.get_json()

        # Ensure category_name is provided
        if 'category_name' not in data:
            return jsonify({'message': 'Category name is required'}), 400
        
        new_category = Category(category_name=data['category_name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'message': 'Category added successfully!', 'category_id': new_category.category_id})

    def patch(self, category_id):
        """Update an existing category partially."""
        data = request.get_json()
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404

        if 'category_name' in data:
            category.category_name = data['category_name']
        
        db.session.commit()
        return jsonify({'message': 'Category updated successfully!'})

    def delete(self, category_id):
        """Delete an existing category."""
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404

        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully!'})

# Define routes for CategoryResource
api.add_resource(CategoryResource, '/categories', '/categories/<int:category_id>')
