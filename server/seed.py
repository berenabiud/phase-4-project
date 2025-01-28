from app import app, db  # Import your Flask app instance and db from the main app file
from models import Game, Category, Player, Country, PlayerGame  # Import your models

def seed_database():
    with app.app_context():  # Create an application context
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()

        # Create sample countries
        usa = Country(country_name="USA")
        japan = Country(country_name="Japan")
        germany = Country(country_name="Germany")

        # Add countries to the session
        db.session.add_all([usa, japan, germany])
        db.session.commit()

        # Create sample categories
        action = Category(category_name="Action")
        rpg = Category(category_name="RPG")
        strategy = Category(category_name="Strategy")

        # Add categories to the session
        db.session.add_all([action, rpg, strategy])
        db.session.commit()

        # Create sample games
        game1 = Game(title="Halo", release_year=2001, photo_url="https://example.com/halo.jpg", category=action)
        game2 = Game(title="Final Fantasy VII", release_year=1997, photo_url="https://example.com/ff7.jpg", category=rpg)
        game3 = Game(title="StarCraft", release_year=1998, photo_url="https://example.com/starcraft.jpg", category=strategy)

        # Add games to the session
        db.session.add_all([game1, game2, game3])
        db.session.commit()

        # Create sample players
        player1 = Player(username="gamer123", email="gamer123@example.com", country=usa)
        player2 = Player(username="pro_player", email="pro@example.com", country=japan)
        player3 = Player(username="casual_gamer", email="casual@example.com", country=germany)

        # Add players to the session
        db.session.add_all([player1, player2, player3])
        db.session.commit()

        # Create sample player-game relationships (reviews and ratings)
        player_game1 = PlayerGame(game=game1, player=player1, review="Amazing game!", rating=4.5)
        player_game2 = PlayerGame(game=game2, player=player2, review="Classic RPG", rating=5.0)
        player_game3 = PlayerGame(game=game3, player=player3, review="Great for strategy fans", rating=4.0)

        # Add player-game relationships to the session
        db.session.add_all([player_game1, player_game2, player_game3])
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
