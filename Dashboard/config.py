import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    CAFE_DATA = os.path.join(os.path.dirname(__file__), 'app', 'data', 'raw', 'corrected_transactions.csv')