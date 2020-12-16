
import time
import os
from hashlib import md5
from datetime import date
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from models import db, User, Category, Purchase
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)


DEBUG = True
SECRET_KEY = 'development key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'budget.db')

app.config.from_object(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #here to silence deprecation warning

db.init_app(app)

categ_dict = {}
#{"DON'T PICK":['demo_user',24, status = 0]}

firstRun = []

purch_dict = {}
#{"demo_purchase":["demo_user",12, "demo_item","99/99/9999", "demoCategory"]}


parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('limit')


class CategoryRest(Resource):
	def get(self):
		print(categ_dict)
		return categ_dict

	def post(self):
		user = User.query.filter_by(user_id=session['user_id']).first()

		args = parser.parse_args()
		name = args['name']
		limit = args['limit']

		newCateg = Category(name,limit, session['user_id'],user.username)
		db.session.add(newCateg)
		db.session.commit()

		temp = [user.username,limit, 0]
		
		categ_dict[name] = temp
		return "", 201

class SingleCategoryRest(Resource):
	def delete(self,categoryId):

		user = User.query.filter_by(user_id=session['user_id']).first()

		categ_dict.pop(categoryId)

		theRealId = get_category_id(categoryId,session['user_id'])

		lisT = Purchase.query.filter_by(categ = theRealId).all()

		for l in lisT:
			purch_dict[l.item][4] = "uncategorized"
			l.categ = None
			l.categcategString = "uncategorized"
			db.session.commit

		category = Category.query.filter_by(category_id = theRealId).first()
		db.session.delete(category)
		db.session.commit

		return '',204



api.add_resource(CategoryRest, '/cats')
api.add_resource(SingleCategoryRest,  "/cats/<categoryId>" )

class PurchaseRest(Resource):
	def get(self):
		return purch_dict

	def post(self):
		user = User.query.filter_by(user_id=session['user_id']).first()


		args = otherParser.parse_args()
		aSpent = int(args["aSpent"])
		item = args["item"]
		date = args["date"]
		theCate = args["category"]
		categId = get_category_id(theCate,session['user_id'])

		newPurchase = Purchase(int(aSpent),item,date,theCate,categId,user.username)
		db.session.add(newPurchase)
		Category.query.filter_by(category_id = categId).first().status += aSpent
		db.session.commit()

		categ_dict[theCate][2] += aSpent
		print(categ_dict)

		temp = [user.username,aSpent,item,date,theCate]
		purch_dict[item] = temp
		return "", 201


otherParser = reqparse.RequestParser()
otherParser.add_argument("aSpent")
otherParser.add_argument("item")
otherParser.add_argument("date")
otherParser.add_argument("category")

api.add_resource(PurchaseRest, '/purchases')


@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.create_all()
	print('Initialized the database.')



def get_user_id(username):
	"""Convenience method to look up the id for a username."""
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None



def get_category_id(category,userID):
	rv = Category.query.filter_by(creator = userID).filter_by(name=category).first()
	return rv.category_id if rv else None



@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()





@app.route("/", methods = ['GET', 'POST'])
def homeFunc():

	if len(firstRun) == 0:
		firstRun.append(1)
		tempyc = Category.query.limit(1).all()
		if tempyc is not None:
			c_s = Category.query.all()
			for item in c_s:
				categ_dict[item.name] = [item.creatorString,item.limit,item.status]

		tempyp = Purchase.query.limit(1).all()
		if tempyp is not None:
			p_s = Purchase.query.all()
			for itemp in p_s:
				#{"demo_purchase":["demo_user",12, "demo_item","99/99/9999", "demoCategory"]}

				purch_dict[itemp.item] = [itemp.user, itemp.price,itemp.item,itemp.date,itemp.categString]


	error = None
	if request.method == 'POST':
		if request.form.get('login_btn') == "LOG IN":
			return redirect(url_for("loginfunc"))
		elif request.form.get('signup_btn') == "SIGN UP":
			return redirect(url_for("signupfunc"))
		

	if g.user is not None:
		categoryLIST = Category.query.filter_by(creator = session['user_id']).all()
		return render_template("home.html",error = error, myLIST = categoryLIST)

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

	return render_template('signup.html', error=error)




@app.route('/login', methods=['GET', 'POST'])
def loginfunc():

	error = None
	if request.method == 'POST':

		user = User.query.filter_by(username=request.form['username']).first()

		if user is None:
			error = 'Invalid username'
		elif not user.password == request.form['password']:
			error = 'Invalid password'
		else:
			flash('You are logged in')
			session['user_id'] = user.user_id
			
			return redirect(url_for('homeFunc'))

	return render_template('loginpage.html', error=error)





@app.route('/logout/')
def logout():
	
	session['user_id'] = None
	return redirect(url_for("homeFunc"))






