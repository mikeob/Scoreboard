import os
import sqlite3
from progteam import *
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'flaskr.db'),
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
	))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60




""" Databse functions """

def connect_db():
	"""Connects to the specific databate."""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()



""" View functions """

@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select title, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute('insert into entries (title, text) values (?, ?)',
		[request.form['title'], request.form['text']])	
	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))

	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

@app.route('/upload', methods=['GET','POST'])
def upload_file():

	if request.method == 'POST':
		f = request.files['file']
		f.save(f.filename)
		print 'Success!'
		flash('File was uploaded successfully')
		return render_template('show_entries.html')

	return render_template('upload.html')

def make_problems(num):
	problems = []
	for count in xrange(num):
		name = "Problem " + `count`
		p = Problem(name, "url")
		problems.append(p)
	return problems

teams = []
problems = []

@app.route('/scoreboard', methods=['GET'])
def new_scoreboard():
	global teams
	global problems

	if len(teams) == 0:
		print 'Making teams/problems!'

		# Generate teams & problems
		problems = make_problems(8)

		team1 = Team("Team 1", problems)
		team1.solved_count = 4
		team1.time = 100
		team1.solved[0] = 2
		team2 = Team("Team 2", problems)
		team2.solved_count = 4
		team2.time = 99

		teams.append(team1)
		teams.append(team2)



	# Sort the teams first by problems solved, then by time
	teams.sort(key=lambda x: (-x.solved_count, x.time))


	return render_template("scoreboard.html",
		teams = teams,
		problems = problems)

@app.route('/scoreboard/<int:problem_id>/<int:solved>')#, methods=['POST'])
def mark_attempt(problem_id, solved):
	print 'Received!'

	teams[0].tries[problem_id] += 1
	if solved == 1:
		teams[0].solved[problem_id] = 100

	return redirect(url_for('new_scoreboard'))


if __name__ == '__main__':
	app.run()