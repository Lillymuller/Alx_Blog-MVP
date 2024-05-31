import jwt
from datetime import datetime, timedelta
from alxblog import db, app, login_manager
from flask_login import UserMixin
from flask import cli, request, jsonify
from sqlalchemy.orm import sessionmaker
from flask_mail import Message


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        payload = {'user_id': self.id}

        encoded_jwt = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        return encoded_jwt
    
    @staticmethod
    def verify_reset_token(token):
        try:
            decoded_payload = jwt.decode(token, app.config['SECRET_KEY'], algorithm='HS256')
            user_id = decoded_payload['user_id']
            return jsonify({'user_id': user_id})
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'})
        except (jwt.InvalidTokenError, jwt.DecodeError):
            return jsonify({'error': 'Invalid token'})

    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

@app.cli.command('initdb')
def initdb_command():
    with app.app_context():
        db.create_all()
        session = db.session
    print('Database table created!')