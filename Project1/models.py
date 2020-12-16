from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

attending = db.Table('attending', 
	db.Column('event_id', db.Integer, db.ForeignKey('event.event_id')), 
	db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')))

# a user(attendee) can attend many events
# an event can have many users(attendee)

class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	pw_hash = db.Column(db.String(64), nullable=False)

	#user can host many events
	hostings = db.relationship('Event', backref = 'hostPerson', lazy = 'dynamic')

	attendees = db.relationship('Event', secondary=attending, backref=db.backref('theAttendees', lazy='dynamic'))	# attendee to user many to many relationship

	def __init__(self, username, pw_hash):
		self.username = username
		self.pw_hash = pw_hash

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Event(db.Model):
	event_id = db.Column(db.Integer, primary_key=True)

	title = db.Column(db.String(50), nullable=False)
	description = db.Column(db.String(100), nullable=False)
	startTime = db.Column(db.DateTime(), nullable = False)
	endTime = db. Column(db.String(20), nullable = False)
	
	host = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

	events = db.relationship('User', secondary=attending, backref=db.backref('events', lazy='dynamic'))
	#user can host many events

	def __init__(self, title, description,startTime,endTime,host):
		self.title = title
		self.description = description
		self.startTime = startTime
		self.endTime = endTime
		self.host = host

	def __repr__(self):
		return '<Event: {}>'.format(self.title)



	

