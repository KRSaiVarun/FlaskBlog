import os

class Config:
    # MongoDB configuration
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/'
    
    # Flask-WTF configuration
    WTF_CSRF_ENABLED = True
    
    # Application configuration
    POSTS_PER_PAGE = 5
