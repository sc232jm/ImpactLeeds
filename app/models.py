from datetime import datetime, timezone
from app import db
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

bcrypt = Bcrypt()


"""
Utilises flask-login: https://flask-login.readthedocs.io/en/latest/ for authentication
Utilises flask-bycrypt: https://flask-bcrypt.readthedocs.io/en/1.0.1/ for password hashing

Strings set at arbitrary sizes to reduce database clutter and mitigate rendering issues
"""

# User model with flask-login UserMixin
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    email = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(16))
    last_name = db.Column(db.String(16))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    about_me = db.Column(db.String(256), nullable=False, default="write something here")
    status_badges = db.Column(db.JSON, nullable=False, default=[])

    petitions = db.relationship('Petition', backref='user', lazy=True)
    signatures = db.relationship('Signature', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# Petition Model
class Petition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    tag_line = db.Column(db.String(32))
    description = db.Column(db.String(1024), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    image_url = db.Column(db.String(128))
    status_badges = db.Column(db.JSON, nullable=False, default=[])

    signatures = db.relationship('Signature', backref='petition', lazy=True)

# Signature (association object) links User to Petition
class Signature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    petition_id = db.Column(db.Integer, db.ForeignKey('petition.id'), nullable=False)
    reason = db.Column(db.String(64))
    is_anonymous = db.Column(db.Boolean, default=False)
    signed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    flagged = db.Column(db.Boolean, default=False)

    likes = db.relationship('Like', backref='signature', lazy=True)

# Like Model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    signature_id = db.Column(db.Integer, db.ForeignKey('signature.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))