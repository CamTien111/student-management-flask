import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///student_mgmt.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False