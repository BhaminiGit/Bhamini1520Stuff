import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, Event


app = Flask(__name__)

# configuration

DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'events.db')

app.config.from_object(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #here to silence deprecation warning

db.init_app(app)


@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.create_all()
	print('Initialized the database.')


def get_user_id(username):
	"""Convenience method to look up the id for a username."""
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

def get_event_id(title):
	rv = Event.query.filter_by( title=title).first()
	return rv.event_id if rv else None

def format_datetime(timestamp):
	"""Format a timestamp for display."""
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')




@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()


@app.route('/')
def show_home():
	
	return render_template('home.html', alleventList = Event.query.order_by(Event.startTime.asc()).all()) #, entries=entries


@app.route('/userHome')
def user_Home():

	if not g.user:
		redirect(url_for('show_home'))

	user = User.query.filter_by(user_id=session['user_id']).first()

	events = [user.user_id]
	userEvents = Event.query.filter(Event.host.in_(events)).order_by(Event.startTime.asc()).all()

	
	return render_template('home.html', usereventList=userEvents, alleventList = Event.query.order_by(Event.startTime.asc()).all())


@app.route('/register', methods=['GET', 'POST'])
def register():
	if g.user:
		return redirect(url_for('user_Home'))
	error = None
	
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
	
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(request.form['username'],  generate_password_hash(request.form['password'])))
			db.session.commit()
			flash('You were successfully registered and can login if you want')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)


@app.route('/logout')
def logout():
	"""Logs the user out."""
	flash('You were logged out')
	session.pop('user_id', None)
	return redirect(url_for('show_home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Logs the user in."""
	if g.user:
		return render_template('home.html', userList = User.query.all())
	error = None
	if request.method == 'POST':

		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid username'
		elif not check_password_hash(user.pw_hash, request.form['password']):
			error = 'Invalid password'
		else:
			flash('You were logged in')
			session['user_id'] = user.user_id
			return redirect(url_for('user_Home'))
	return render_template('login.html', error=error)


@app.route('/hostEvent',methods=['GET','POST'])
def host():
	if 'user_id' not in session:
		abort(401)

	error = None
	if request.method == 'POST':
		if not request.form["eventTitle"]:
			error = "Enter a title"
		elif not request.form["eventDes"]:
			error = "Enter a description"
		elif not request.form["startDT"]:
			error = "Enter a start time"
		elif not request.form["endDT"]:
			error = "Enter an end time"
		else:

			starting = datetime.strptime(request.form["startDT"],'%Y-%m-%dT%H:%M')
			ending = datetime.strptime(request.form["endDT"],'%Y-%m-%dT%H:%M')
			eventAdding = Event(request.form["eventTitle"], request.form["eventDes"], starting, ending, session['user_id'])
			db.session.add( eventAdding )
			db.session.commit()

			
			flash("Event added")
			return redirect(url_for('user_Home'))

	return render_template('eventCreation.html',error = error)



@app.route('/<event_title>/cancelEvent')
def cancelEvent(event_title):

	if not g.user:
		abort(401)

	cancel_id = get_event_id(event_title)
	if cancel_id is None:
		abort(401)

	event_cancel = Event.query.filter_by(event_id = cancel_id).first()
	return render_template('eventCancel.html',eventThing = event_cancel )



	

@app.route('/<event_title>/cancelEvent_sure')
def cancelEvent_sure(event_title):

	if not g.user:
		abort(401)

	cancel_id = get_event_id(event_title)
	if cancel_id is None:
		abort(401)

	event_cancel = Event.query.filter_by(event_id = cancel_id).first()
	
	db.session.delete(event_cancel)

	db.session.commit()
	flash("You have successfully canceled the event")

	return redirect(url_for('user_Home'))


@app.route('/<event_title>/attendEvent')
def attendEvent(event_title):
	#arguement will be event that we want to attend

	if not g.user:
	 	abort(401)

	theEventId = get_event_id(event_title)

	theUser = User.query.filter_by(user_id=session['user_id']).first()
	theEvent = Event.query.filter_by(event_id = theEventId).first()

	if theEvent not in theUser.events:
		theEvent.events.append(theUser)
		db.session.commit()
		flash("You are now attending the event")
	else:
		flash("You are already attending the event!!!!")


	# #theUser is the the current user that will be appeneded to the attendees of the event 
	

	

	return redirect(url_for('user_Home'))










############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################




# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
