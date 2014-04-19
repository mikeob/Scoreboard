



''' Team class. Represents
	a programming team. Has
	a copy of the problems, and their
	times for solving them.
'''
class Team:
	def __init__(name, problems):
		self.name = name	 # Name of the team
		self.problems = problems # Array of problem names
		self.solved = [-1] * problems.len()  # Time problem solved. -1 if not solved.
		self.tries = [0] * problems.len()



''' Problem class. Represents
	a programming problem. 

	Contains the name and url for the problem,
	as well as other meta-data
'''
class Problem:
	def __init__(name, url):
		self.name = name
		self.url = url

