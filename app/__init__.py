from flask import Flask

def create_app():
    app = Flask(__name__)

    # Configurations
    from config import Config
    app.config.from_object(Config)

    # Initialize JWT with the app
    from flask_jwt_extended import JWTManager
    
    jwt = JWTManager(app)

    # Import and register blueprints
    from app.auth.routes import auth_bp
    from app.book.routes import book_bp
    from app.review.routes import review_bp

    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(book_bp, url_prefix='/book')
    app.register_blueprint(review_bp, url_prefix='/review')

    return app
