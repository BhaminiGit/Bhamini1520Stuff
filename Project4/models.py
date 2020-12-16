
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False)
	password = db.Column(db.String(20), nullable=False)
	categories = db.relationship('Category',backref = 'category', lazy = 'dynamic')

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Category(db.Model):
	category_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), nullable=False)
	limit = db.Column(db.Integer, nullable=False)
	creator= db.Column(db.Integer, db.ForeignKey('user.user_id'))
	creatorString = db.Column(db.String(30), nullable=False)
	status = db.Column(db.Integer,nullable = False)
	purchases = db.relationship('Purchase', backref = 'purchase', lazy = 'dynamic')

	

	def __init__(self,name,limit,creator,creatorString):
		self.name = name
		self.limit = limit
		self.creator = creator
		self.creatorString = creatorString
		self.status = 0 #amount of money spent in this category


	def __repr__(self):
		return '{}, limit: ${}'.format(self.name,self.limit)

class Purchase(db.Model):
	purchase_id = db.Column(db.Integer, primary_key=True)
	price = db.Column(db.Integer, nullable=False)
	item = db.Column(db.String(30), nullable=False)
	date = db.Column(db.String(40), nullable=False)
	categString = db.Column(db.String(30))

	categ = db.Column(db.Integer, db.ForeignKey('category.category_id'))
	user = db.Column(db.String(30),nullable=False)

	def __init__(self,price,item,date,categString,categ,user):
		self.price = price
		self.item = item
		self.date = date
		self.categString = categString
		self.categ = categ
		self.user = user

	def __repr__(self):
		return 'name: {}'.format(self.item)

