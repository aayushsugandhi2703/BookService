from secret import get_secret_key

class Config:
    SECRET_KEY = get_secret_key()
    JWT_SECRET_KEY = get_secret_key()
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = False
    JWT_ACCESS_TOKEN_EXPIRES = True
    JWT_ACCESS_TOKEN_EXPIRES = 1000  
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
