
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON


db = SQLAlchemy()


class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120))
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(300))

class Auth(db.Model):
	__tablename__ = "auths"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer)
	log_in = db.Column(db.DateTime, default=datetime.datetime.now)
	log_out = db.Column(db.DateTime, nullable=True)




