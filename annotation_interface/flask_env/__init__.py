from flask import Flask, render_template, request, redirect, session, url_for, make_response
from flask_pymongo import PyMongo
from flask_env.forms import LoginForm
from bson import json_util, objectid
import json

app = Flask(__name__)
app.config.from_object('config')

mongo = PyMongo()

mongo.init_app(app)

client = mongo.cx
db = client.beta_db
user_db = client.user_db
comments = db.comments

@app.route('/')
def start():

	# redirect to login page
	return redirect(url_for('login'))

@app.route('/login/', methods = ['GET', 'POST'])
def login():

	"""
	gets username from login form. stores username in session as 'alias'
	"""
	users = user_db.users
	form = LoginForm()

	if form.validate_on_submit():
		login_user = users.find_one({'name' : form.data['name'].lower()})
		if login_user:
			session['alias'] = login_user['alias']
			return redirect(url_for('load'))
	return render_template('login.html', form = form) 

@app.route('/logout/')
def logout():

	"""
	logs current user out -- removes username from session
	"""
	session['alias'] = None
	return redirect(url_for('login'))

@app.route('/done/')
def done():

	"""
	when user has labelled all comments -- removes username from session 
	"""
	session['alias'] = None
	return "Thanks all done."

@app.route('/load', methods = ['GET'])
def load():

	"""
	load the next comment for the user to annotate and redirect to annotation form
	"""
	if 'alias' in session:
		try:
			document = get_next_comment(session['alias'])
		except IndexError: 
			return redirect(url_for('done'))
	
		document = json.loads(json_util.dumps(document)) 
		comment = document['comment']
		session['doc_id'] = document['_id']
		print(session['doc_id'])
	else: 
		return redirect(url_for('login'))
	
	return redirect(url_for('index', comment_text = comment))

@app.route('/<comment_text>', methods = ['GET', 'POST'])
def index(comment_text):

	"""
	display comment for annoation and receive annoation from annotation form

	Arguments:
	comment_text -- text of the comment for annotation
	"""

	if 'alias' in session:
		annotatorID = session['alias']
	else: 
		return redirect(url_for("login"))

	if request.method == "POST":

		label = request.form.get('beta_label')
		if label is not None:
			print("{} says believes the label for {} is {}".format(annotatorID, comment_text,label))
			print(update_label(session['doc_id'], annotatorID, int(label)))
		return redirect(url_for('load'))
			
	return render_template('annotation_form.html', comment = comment_text)

def get_random_comment():

	"""
	gets one random comment from the comment database

	Returns: 
	text of random comment

	"""

	random_comment = list(comments.aggregate([{'$sample': {'size' : 1}}]))[0]['comment']
	return random_comment 

def get_next_comment(annotator_alias):

	"""
	gets one comment that has been queried by the active learner but has not
	been labelled by the annotator
	
	Arguments: 
	annotator_alias  -- the alias of the current annotator

	Returns: 
	document from the comment database
	"""

	# find a comment that has not been labelled by annotator but has been queried. 
	query = {"final_test" : 1, annotator_alias: None}
	# match and random sample to get one random comment that matches query
	match = {"$match" : query }
	random_sample = {"$sample" : {"size" : 1}}
	next_comment = list(comments.aggregate([match, random_sample]))[0]
	return next_comment

def update_label(comment_id, annotator_alias, label):

	"""
	updates the comment document to contain the label for the given annotator under the 
	field annotator_alias

	Arguments: 
	comment_id -- the document id for the comment to be updated
	annotator_alias -- the alias for the current annotator
	label -- the label to update the comment with
	"""

	doc_id = objectid.ObjectId(comment_id['$oid'])
	query = { '_id' : doc_id }
	update = {"$set": {annotator_alias : label}}
	return comments.update_one(query, update)


