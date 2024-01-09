from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

user_domain_association = db.Table(
    'user_domain_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('domain_id', db.Integer, db.ForeignKey('domain.id'), primary_key=True)
)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(250), unique=True, nullable=False)
	password = db.Column(db.String(250), nullable=False)
	salt = db.Column(db.String(16), nullable=False)
	api_key = db.Column(db.String(64), unique=True, nullable=False)
	registered_on = db.Column(db.DateTime, nullable=False)

	domains = db.relationship('Domain', secondary=user_domain_association, back_populates='users')
	
class Domain(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	domain_name = db.Column(db.String(250), unique=True, nullable=False)
	target = db.Column(db.String(250), nullable=True)
	analysis = db.Column(db.String(16), nullable=True)
	other_targets = db.Column(db.String(1000), nullable=True)
	evaluated_on = db.Column(db.DateTime, nullable=True)

	users = db.relationship('User', secondary=user_domain_association, back_populates='domains')

