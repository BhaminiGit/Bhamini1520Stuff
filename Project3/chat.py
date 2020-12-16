from flask import Flask, render_template, request, redirect,url_for,flash,session,g
from models import db, User
import os
import json

app = Flask(__name__)
# configuration

DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')

app.config.from_object(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #here to silence deprecation warning

db.init_app(app)


chatroomList = ["Demo Chat 0"]

items = [["demo message 0"], ["demo message 1"]]

loggedIn = [];



@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.create_all()
	print('Initialized the database.')


def get_user_id(username):
	"""Convenience method to look up the id for a username."""
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None



@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()


@app.route("/", methods = ['GET', 'POST'])
def homeButtons():

	if request.method == 'POST':
		if request.form.get('login') == "login":
			return redirect(url_for("loginfunc"))

		elif request.form.get('signup') == "signup":
			return redirect(url_for("signupfunc"))

	return render_template("home.html")



@app.route('/signup', methods=['GET', 'POST'])
def signupfunc():
	
	error = None
	
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
	
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:

			

			db.session.add(User(request.form['username'], request.form['password']))
			db.session.commit()
			flash('You were successfully registered and can login if you want')
			return redirect(url_for('loginfunc'))

	return render_template('signup.html', error=error, userList = loggedIn)



@app.route('/login', methods=['GET', 'POST'])
def loginfunc():
	
	error = None
	if request.method == 'POST':

		user = User.query.filter_by(username=request.form['username']).first()

		if user is None:
			error = 'Invalid username'
		elif not user.password == request.form['password']:
			error = 'Invalid password'
		elif user.username in loggedIn:
			error = "You're already logged in!"
		else:
			flash('You are logged in')
			session['user_id'] = user.user_id
			
			loggedIn.append(user.username);
			return redirect(url_for('chatroomsFunc'))

	return render_template('login.html', error=error, userList = loggedIn)


@app.route('/logout/<username>')
def logout(username):
	
	loggedIn.remove(username)
	if(len(loggedIn) > 0  ):

		session["user_id"] = get_user_id(loggedIn[0])
		return redirect(url_for(chatroomsFunc))
	else:
		return redirect(url_for("homeButtons"))



@app.route('/chatrooms')
def chatroomsFunc():

	user = User.query.filter_by(user_id=session['user_id']).first()

	return render_template("chatrooms.html",currentUser = user.username, chatrooms = chatroomList, userList = loggedIn)




@app.route('/currentChat/<roomName>/<roomNum>',methods= ["GET", "POST"])
def currentChatFunc(roomName,roomNum):

	if request.method == "GET":
		user = User.query.filter_by(user_id=session['user_id']).first()

		return render_template("currentChat.html",items = items, currentUser = user.username, roomNum = roomNum, roomName = roomName, userList = loggedIn);



@app.route("/new_item/", methods=["POST"])
def add():

	items[int(request.form["num"])].append(request.form["one"])
	return "OK!"

@app.route("/messages")
def get_items():
	return json.dumps(items)


@app.route('/room/createNewRoom', methods = ["GET", "POST"])
def createRoom():

	user = User.query.filter_by(user_id=session['user_id']).first()

	error = "";


	if request.method == "POST":

		newRoom = request.form['roomName']

		chatroomList.append(newRoom)
		items.append([])	
		

		return redirect(url_for("chatroomsFunc"))


	return render_template("createChatroom.html",currentUser = user.username, userList = loggedIn)


@app.route('/leaveRoom')
def leaveRoom():

	return redirect(url_for("chatroomsFunc"))


@app.route('/switchUsers/<username>')
def switchUsers(username):
	cu = get_user_id(username)
	session['user_id'] = cu
	return redirect(url_for("chatroomsFunc"))








