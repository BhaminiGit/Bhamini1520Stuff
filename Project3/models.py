from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	password = db.Column(db.String(64), nullable=False)

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __repr__(self):
		return '<User {}>'.format(self.username)



