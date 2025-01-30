#!/usr/bin/env python3
import os
from flask import Flask, jsonify  # ✅ Import jsonify here
from flask_migrate import Migrate
from flask_restful import Api, Resource, request  # ✅ Import Resource here
from flask_cors import CORS
from models import db, Game, Player, PlayerGame, Category, Country
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)

# Enable CORS
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Enable CORS for specific routes (e.g., /api/*)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize JWTManager
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "123456")  # Add a default key if not in env
jwt = JWTManager(app)

# Initialize database and migrations
migrate = Migrate(app, db)
db.init_app(app)

# Initialize API
api = Api(app)

@app.route("/")
def index():
    return "<h1>Hi Welcome</h1>"



class GameResource(Resource):
    def get(self, game_id=None):
        try:
            if game_id:
                # Retrieve a single game by ID
                game = Game.query.get(game_id)
                if game:
                    return {  # ✅ Return a dictionary (Flask-Restful auto-serializes it)
                        'game_id': game.game_id,
                        'title': game.title,
                        'release_year': game.release_year,
                        'photo_url': game.photo_url,
                        'category': game.category.category_name if game.category else None
                    }, 200
                return {"message": "Game not found"}, 404  # ✅ Dict + Status Code

            else:
                # Retrieve all games if no game_id is provided
                games = Game.query.all()
                return [{
                    'game_id': game.game_id,
                    'title': game.title,
                    'release_year': game.release_year,
                    'photo_url': game.photo_url,
                    'category': game.category.category_name if game.category else None
                } for game in games], 200  # ✅ List of dictionaries

        except Exception as e:
            return {"error": str(e)}, 500  # ✅ Dict + Status Code


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



class CategoryResource(Resource):
    def get(self, category_id=None):
        """Retrieve a specific category by its ID or all categories."""
        if category_id:
            # Retrieve a single category by ID
            category = Category.query.get(category_id)
            if category:
                # Get all games that belong to this category
                games = Game.query.filter_by(category_id=category_id).all()
                return jsonify({
                    'category_id': category.category_id,
                    'category_name': category.category_name,
                    'games': [{
                        'game_id': game.game_id,
                        'title': game.title,
                        'release_year': game.release_year,
                        'photo_url': game.photo_url
                    } for game in games]
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


from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

class PlayerResource(Resource):
    def get(self, player_id=None):
    
     if player_id:
        # Retrieve a specific player by ID
        player = Player.query.get(player_id)
        if not player:
            return jsonify({'message': 'Player not found'}), 404
        
        # Return player details including password_hash
        return jsonify({
            'player_id': player.player_id,
            'username': player.username,
            'email': player.email,
            'country': player.country.country_name,
            'password_hash': player.password_hash  # Optional: include password_hash
        })
     else:
        # Retrieve all players
        players = Player.query.all()
        if not players:
            return jsonify({'message': 'No players found'}), 404
        
        # Return player details including password_hash
        players_data = [{
            'player_id': player.player_id,
            'username': player.username,
            'email': player.email,
            'country': player.country.country_name,
            'password_hash': player.password_hash  # Optional: include password_hash
        } for player in players]
        
        return jsonify(players_data)


    def post(self):
        """Create a new player."""
        data = request.get_json()

        # Ensure required fields are present
        if not all(field in data for field in ['username', 'email', 'password', 'country_id']):
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if the username or email already exists
        existing_user = Player.query.filter((Player.username == data['username']) | (Player.email == data['email'])).first()
        if existing_user:
            return jsonify({'message': 'Username or email already taken'}), 400

        # Hash the password before storing it
        hashed_password = generate_password_hash(data['password'])

        # Create new player with hashed password
        new_player = Player(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password,
            country_id=data['country_id']
        )
        
        # Save the new player to the database
        db.session.add(new_player)
        db.session.commit()
        
        return jsonify({'message': 'Player added successfully!', 'player_id': new_player.player_id})

    def patch(self, player_id):
        """Update an existing player partially."""
        data = request.get_json()

        player = Player.query.get(player_id)
        if not player:
            return jsonify({'message': 'Player not found'}), 404
        
        if 'username' in data:
            player.username = data['username']
        if 'email' in data:
            player.email = data['email']
        if 'country_id' in data:
            player.country_id = data['country_id']
        if 'password' in data:  # If password is being updated
            # Hash the new password
            player.password_hash = generate_password_hash(data['password'])
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({'message': 'Player updated successfully!'})

    
class CountryResource(Resource):
    def get(self, country_id=None):
        if country_id:
            country = Country.query.get(country_id)
            if not country:
                return jsonify({'message': 'Country not found'}), 404

            # Retrieve all players associated with this country
            players = [{'player_id': player.player_id, 'username': player.username} for player in country.players]

            return jsonify({
                'country_id': country.country_id,
                'country_name': country.country_name,
                'players': players  # Include players in the response
            })

        # Retrieve all countries (if no country_id is provided)
        countries = Country.query.all()
        if not countries:
            return jsonify({'message': 'No countries found'}), 404

        return jsonify({'countries': [  # Corrected indentation here
            {'country_id': country.country_id, 'country_name': country.country_name}
            for country in countries
        ]})

    def post(self):
        """Create a new country."""
        data = request.get_json()
        if not data or 'country_name' not in data:
            return jsonify({'message': 'Missing country_name in request'}), 400
        
        new_country = Country(country_name=data['country_name'])
        db.session.add(new_country)
        db.session.commit()
        return jsonify({'message': 'Country added successfully!', 'country_id': new_country.country_id}), 201

    def patch(self, country_id):
        """Update an existing country partially."""
        data = request.get_json()
        country = Country.query.get(country_id)
        if not country:
            return jsonify({'message': 'Country not found'}), 404
        
        if 'country_name' in data:
            country.country_name = data['country_name']
        
        db.session.commit()
        return jsonify({'message': 'Country updated successfully!'})
    
class CountryPlayersResource(Resource):
    def get(self, country_id):
        """Retrieve all players of a specific country"""
        country = Country.query.get(country_id)
        if not country:
            return jsonify({'message': 'Country not found'}), 404

        players = [{'player_id': player.player_id, 'username': player.username} for player in country.players]
        return jsonify({'country_id': country.country_id, 'country_name': country.country_name, 'players': players})

class PlayerGameResource(Resource):
    
    # Get a specific player-game relationship or all player-game relationships
    def get(self, player_game_id=None):
        if player_game_id:
            # Retrieve a single player-game relationship by player_game_id
            player_game = PlayerGame.query.get(player_game_id)
            if not player_game:
                return jsonify({'message': 'PlayerGame not found'}), 404
            
            # Return the details of the player-game relationship
            return jsonify({
                'id': player_game.id,
                'game': player_game.game.title,
                'player': player_game.player.username,
                'review': player_game.review,
                'rating': player_game.rating
            })
        
        # Retrieve all player-game relationships if no player_game_id is provided
        player_games = PlayerGame.query.all()
        if not player_games:
            return jsonify({'message': 'No player-game relationships found'}), 404
        
        # Return all player-game relationships
        return jsonify([{
            'id': player_game.id,
            'game': player_game.game.title,
            'player': player_game.player.username,
            'review': player_game.review,
            'rating': player_game.rating
        } for player_game in player_games])
    

    # Create a new player-game relationship
    def post(self):
        data = request.get_json()
        
        # Validate incoming data
        if not data or 'game_id' not in data or 'player_id' not in data:
            return jsonify({'message': 'Missing required fields (game_id, player_id)'}), 400
        
        # Create the new player-game relationship
        new_player_game = PlayerGame(
            game_id=data['game_id'],
            player_id=data['player_id'],
            review=data.get('review'),
            rating=data.get('rating')
        )
        
        # Add to session and commit to the database
        db.session.add(new_player_game)
        db.session.commit()
        
        # Return success message
        return jsonify({'message': 'PlayerGame added successfully!', 'id': new_player_game.id}), 201
    

    # Partially update an existing player-game relationship
    def patch(self, player_game_id):
        data = request.get_json()
        
        # Find the player-game relationship by ID
        player_game = PlayerGame.query.get(player_game_id)
        if not player_game:
            return jsonify({'message': 'PlayerGame not found'}), 404
        
        # Update only the fields that are provided
        if 'review' in data:
            player_game.review = data['review']
        if 'rating' in data:
            player_game.rating = data['rating']
        
        # Commit changes to the database
        db.session.commit()
        
        # Return success message
        return jsonify({'message': 'PlayerGame updated successfully!'})
    
from flask import request
from flask_restful import Resource
from models import Game, Player  # Ensure you import the models appropriately

class PlayerGamesResource(Resource):
    def get(self, player_id):
        # Retrieve the player from the database
        player = Player.query.get(player_id)
        if not player:
            return {'message': 'Player not found'}, 404

        # Retrieve games associated with the player (adjust based on your model)
        games = Game.query.filter_by(player_id=player_id).all()

        # If no games are found for the player
        if not games:
            return {'message': 'No games found for this player'}, 404

        # Format the list of games to return as JSON
        games_data = [{'game_id': game.id, 'name': game.name, 'genre': game.genre} for game in games]

        return {'games': games_data}, 200


from flask import request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from models import Player  # Adjust the import path as necessary

class LoginResource(Resource):
    def post(self):
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'password']
        if not all(field in data for field in required_fields):
            return {'message': 'Missing fields'}, 400

        username = data['username']
        password = data['password']

        # Retrieve player by username
        player = Player.query.filter_by(username=username).first()
        if not player:
            print(f"Player not found: {username}")
            return {'message': 'Invalid username or password'}, 401

        # Check if the password matches
        if not player.check_password(password):
            print(f"Invalid password for player: {username}")
            return {'message': 'Invalid username or password'}, 401

        try:
            # Create access token
            access_token = create_access_token(identity=player.player_id)
            print(f"Access token created: {access_token}")

            # Ensure player data is being passed
            user_data = {
                'username': player.username,
                'email': player.email,  # Adjust based on your Player model
            }
            print(f"User data: {user_data}")

            # Return success response with user data and token
            return {
                'user': user_data,
                'access_token': access_token
            }, 200
        except Exception as e:
            print(f"Error generating token: {str(e)}")
            return {'message': f'Error generating token: {str(e)}'}, 500


# Adding the Login route to the API
api.add_resource(LoginResource, '/login')

# Define routes for GameResource
api.add_resource(GameResource, '/games', '/games/<int:game_id>')
api.add_resource(PlayerResource, '/players', '/players/<int:player_id>')
# api.add_resource(GameResource, '/players/<int:player_id>/games')
api.add_resource(CountryResource, '/countries', '/countries/<int:country_id>')
api.add_resource(CountryPlayersResource, '/countries/<int:country_id>/players')
api.add_resource(PlayerGameResource, '/player_games', '/player_games/<int:player_game_id>')
api.add_resource(PlayerGamesResource, '/players/<int:player_id>/games')
