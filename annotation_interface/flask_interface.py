from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm 
from wtforms import StringField, validators
from flask-login import LoginManager()

mongo = PyMongo()
login_manager = LoginManager()
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://eoghan:Ailbhe123@fypcluster-cqcwt.mongodb.net/test?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = "somekey"
login_manager.init_app(app)
mongo.init_app(app)

client = mongo.cx
db = client.beta_db
comments = db.comments

comment = 'Submit YES to get started.'

class LoginForm(FlaskForm):
	name = StringField('username', validators = [validators.DataRequired()])

@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
#		login_user(user)
		flask.flash('Loggin in successfully.')		

		return redirect(flask.url_for('index'))

	return render_template('login.html', form = form)



@app.route('/', methods = ['GET', 'POST'])
def index():
	global comment
	# check annotator ID
	if not request.cookies.get('id'): 
		print("no id set")
		redirect(url_for('login'))
	else:
		print("annotatorID is set")
		annotatorID = request.cookies.get('id')

	if request.method == "POST":

		label = request.form.get('beta_label')
		print("Annotator {} believes the label is {}".format(annotatorID,label))

		if label is not None :
			try:
				comment = random_comment()
			except StopIteration: 
				return "That's all, thanks."
		return render_template('sample_form.html', comment = comment)
	
	return render_template('sample_form.html', comment = comment)

@app.route('/reset/')
def reset():
	res = make_response('Annotator ID removed.')
	res.set_cookie('id', 'temp', max_age = 0)
	return res

def random_comment():
	return list(comments.aggregate([{'$sample': {'size' : 1}}]))[0]['comment']

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = '80', debug = True)
