import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from main import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # Define relationship with posts - one user can have many posts
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @classmethod
    def create_user(cls, username, email, password):
        """Create a new user and insert into the database"""
        user = cls(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def get_by_username(cls, username):
        """Find user by username"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_id(cls, user_id):
        """Find user by ID"""
        return cls.query.get(int(user_id))
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    @classmethod
    def create_post(cls, title, content, author_id):
        """Create a new blog post"""
        post = cls(
            title=title,
            content=content,
            author_id=author_id
        )
        db.session.add(post)
        db.session.commit()
        return post
    
    @classmethod
    def get_by_id(cls, post_id):
        """Find post by ID"""
        try:
            return cls.query.get(int(post_id))
        except (ValueError, Exception) as e:
            import logging
            logging.error(f"Error retrieving post: {e}")
            return None
    
    @classmethod
    def get_all_posts(cls, page=1, per_page=5):
        """Get all posts with pagination"""
        return cls.query.order_by(cls.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False).items
    
    @classmethod
    def get_user_posts(cls, author_id):
        """Get all posts by a specific user"""
        return cls.query.filter_by(author_id=author_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def count_posts(cls):
        """Count total number of posts"""
        return cls.query.count()
    
    def update(self, title, content):
        """Update an existing post"""
        self.title = title
        self.content = content
        # updated_at will be automatically updated due to onupdate=func.now()
        db.session.commit()
    
    def delete(self):
        """Delete a post"""
        db.session.delete(self)
        db.session.commit()
    
    def get_author(self):
        """Get the author of the post"""
        return self.author
