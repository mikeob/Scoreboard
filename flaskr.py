from datetime import datetime
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
start_time = None

@app.route('/scoreboard/start')#, methods=['POST'])
def begin_competition():
	global start_time
	print 'Competition begun!'
	start_time = datetime.now()
	return redirect(url_for('new_scoreboard'))

''' Returns the current time in minutes '''
def get_time():
	global start_time
	if start_time == None:
		return None
	delta = datetime.now() - start_time
	return delta

@app.route('/scoreboard', methods=['GET'])
def new_scoreboard():
	global teams
	global problems

	"""
	if len(teams) == 0:
		print 'Making teams/problems!'

		#TODO Remove once we've added 
		# add_team() and add_problem()
		problems = make_problems(10)

		team1 = Team("Team 1", problems)
		team1.solved_count = 0
		team1.time = 0

		teams.append(team1)
		"""

	# Sort the teams first by problems solved, then by time
	sortedOrder = sorted(teams, key=lambda x: (-x.solved_count, x.time))
	timestring = str(get_time()).split(".")[0]


	return render_template("scoreboard.html",
		teams = sortedOrder,
		problems = problems,
		time = timestring)

@app.route('/add_team', methods=['POST'])
def add_team():
	teamname = request.form['teamname']
	teams.append(Team(teamname, problems))
	teams[len(teams)-1].index = len(teams)-1
	return redirect(url_for('new_scoreboard'))



@app.route('/add_problem', methods=['POST'])
def add_problem():
	problem = request.form['problemname']
	problems.append(Problem(problem, "fakeurl"))
	for team in teams:
		team.add_problem()
	return redirect(url_for('new_scoreboard'))


@app.route('/scoreboard/<int:problem_id>/<int:solved>/<teamidx>')#, methods=['POST'])
def mark_attempt(problem_id, solved, teamidx):
	global start_time

	# If time not started yet...
	if start_time == None:
		flash('Need to start the timer before making attempts')		
		return redirect(url_for('new_scoreboard'))
	if len(teams) == 0:
		flash('No teams currently in the competition')
		return redirect(url_for('new_scoreboard'))

	# Select which team to change
	team = teams[int(teamidx)]
	team.tries[problem_id] += 1

	if solved == 1:
		time = int(get_time().seconds/60)
		team.solved[problem_id] = time
		team.time += time + 20*(team.tries[problem_id]-1)
		team.solved_count += 1

	return redirect(url_for('new_scoreboard'))


if __name__ == '__main__':
	app.run()