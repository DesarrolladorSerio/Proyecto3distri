import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Base de datos
    DB_HOST = os.getenv('DB_HOST', 'mysql_primary')
    DB_USER = os.getenv('DB_USER', 'admin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin')
    DB_DATABASE = os.getenv('DB_DATABASE', 'app3')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    PORT = int(os.getenv('PORT', 3003))
    
    # Middleware
    MIDDLEWARE_URL = os.getenv('MIDDLEWARE_URL', 'http://middleware:8000')
