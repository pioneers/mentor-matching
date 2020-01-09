"""
Main script for running mentor matching
Usage:
	1) Create csv files called "mentors.csv" and "teams.csv", formatted as described in utils.py
	2) Run this program
Three files will be created:
	1) "matching.csv", which contains the matching from mentors to teams (todo)
	2) "team_compatibility.csv", which contains the compatibility matrix between teams and mentors (todo)
	3) "mentor_compatibility.csv", which contains the compatibility matrix for pairs of mentors (todo)


Description of the convex optimization problem:
	Variables:
		(1) One boolean variable for each mentor-team pair, representing if that mentor is paired with that team and is alone
		(2) One boolean variable for each mentor-team pair, representing if that mentor AND at least one other are paired with that team
	Constraints:
		(1) The sum of a team's type (2) variables plus twice the sum of its type (1) variables must be at least 2
				This ensures that if only one mentor is assigned to the team, the corresponding type (1) variable must be active instead of the type (2)
		(2) The sum of a mentor's type (1) and (2) variables is exactly 1
				This ensures that a mentor gets matched with exactly one team
		(3) The sum of a team's type (1) and (2) variables is between minNumMentors and maxNumMentors
				This ensures that a team gets an appropriate number of mentors
		(4) For every mentor-mentor pair that is required to be together, the sum of all their type (1) variables must be zero
				This ensures that mentors that are supposed to be paired don't end up alone
		(5) For every mentor-mentor pair that is required to be together, the sum over the teams of the squared differences between 
			the type (2) variables for these two mentors must be zero.
				This ensures that the mentors will be assigned together.  If they are assigned to two different teams, the two corresponding
				squared differences will be 1; if they are assigned to the same team, all differences will be zero.  This all assumes that they
				aren't assigned using type (1) variables, which constraint type (4) ensures.
	Objective Function Terms:
		(1) For each type (1) variable, score the compatibility for that mentor-team pair minus the cost for the mentor being alone
		(2) For each type (2) variable, score the compatibility for that mentor-team pair

Note that based on how the constraints are set up, there is nothing to stop the program from using type (1) variables when there are actually
	multiple mentors assigned to that team.  However, as it is currently set up, you can only incur an extra cost by doing that, so there's no
	reason for the program to do so.  But this does mean that we can only ever have solo-mentoring incur a cost--we can never treat it as
	adding value without changing the structure of the constraints.

Note also that the constraints of type (5) are fairly resource-intensive, so each mentor pair we require to be paired adds approximately
	4 seconds to the computation time (from a baseline of about half a second if there are no such pairs).  So we should try to minimize
	the number of pairs we require to be together where possible.
"""

import cvxpy as cp
from cvxpy.atoms.elementwise.maximum import maximum # allows us to create an expression that is the maximum of other expressions
import utils
from utils import Mentor, Team
import csv

import time # for testing purposes


print("Process started!  Reading mentor file...", flush = True)
mentors = []
with open("mentors.csv") as mentorFile:
	mentorReader = csv.reader(mentorFile)
	# remove header rows, if any
	for _ in range(utils.mentorHeaderRows):
		next(mentorReader) # just read the row and throw it away
	for dataRow in mentorReader:
		mentors.append(Mentor(dataRow)) # create a new mentor object based on each row of data

print("Reading team file...", flush = True)
teams = []
with open("teams.csv") as teamFile:
	teamReader = csv.reader(teamFile)
	# remove header rows, if any
	for _ in range(utils.teamHeaderRows):
		next(teamReader) # throw out header rows
	for dataRow in teamReader:
		teams.append(Team(dataRow)) # create the team object

print("Creating optimization variables...", flush = True)
variables = [] # list of all variables
varByType = {} # map from variable type to list of variables of that type
varByMentor = {} # map from (variable type, mentor) to list of variables of that type for that mentor
varByTeam = {} # map from (variable type, team) to list of variables of that type for that team
varByPair = {} # map from (variable type, mentor, team) to list of variable of that type for that team and mentor
groupByVar = {} # map from a variable to the (variable type, mentor, team) corresponding to it
# initialize varByType, varByMentor, varByTeam, and varByPair with empty lists to prevent KeyErrors later
for varType in [1, 2]:
	varByType[varType] = []
	for mentor in mentors:
		varByMentor[(varType, mentor)] = []
		for team in teams:
			varByPair[(varType, mentor, team)] = []
	for team in teams:
		varByTeam[(varType, team)] = []
# create variables
for varType in [1, 2]:
	for mentor in mentors:
		for team in teams:
			newVar = cp.Variable(boolean = True)
			variables.append(newVar)
			varByType[varType].append(newVar)
			varByMentor[(varType, mentor)].append(newVar)
			varByTeam[(varType, team)].append(newVar)
			varByPair[(varType, mentor, team)].append(newVar)
			groupByVar[newVar] = (varType, mentor, team)

print("Creating constraints...", flush = True)
constraints = []
# create type (1) constraints
for team in teams:
	typeOneVars = varByTeam[(1, team)]
	typeTwoVars = varByTeam[(2, team)]
	constraints.append(sum(typeTwoVars) + (2 * sum(typeOneVars)) >= 2)
# create type (2) constraints
for mentor in mentors:
	typeOneVars = varByMentor[(1, mentor)]
	typeTwoVars = varByMentor[(2, mentor)]
	constraints.append(sum(typeOneVars) + sum(typeTwoVars) == 1)
# create type (3) constraints
for team in teams:
	typeOneVars = varByTeam[(1, team)]
	typeTwoVars = varByTeam[(2, team)]
	constraints.append(sum(typeOneVars) + sum(typeTwoVars) >= utils.minNumMentors)
	constraints.append(sum(typeOneVars) + sum(typeTwoVars) <= utils.maxNumMentors)
# create type (4) and (5) constraints
for mentor1 in mentors:
	for mentor2 in mentors:
		if mentors.index(mentor1) >= mentors.index(mentor2):
			# we only want to consider each pair once, so ignore the second occurrence
			# this also ensures that we don't consider pairing a mentor with themself
			continue
		if mentor1.mustPair(mentor2) or mentor2.mustPair(mentor1):
			# these mentors are required to be paired, so create the constraints for them
			constraints.append(sum(varByMentor[(1, mentor1)]) + sum(varByMentor[(1, mentor2)]) == 0) # type (4) constraint
			diffTerms = [] # terms in the summation of differences for this constraint
			for team in teams:
				mentor1Var = varByPair[(2, mentor1, team)][0] # get type (2) variables for these mentors and this team
				mentor2Var = varByPair[(2, mentor2, team)][0] # there will only be one variable in each list, so extract it
				diffTerms.append((mentor1Var - mentor2Var)**2)
			constraints.append(sum(diffTerms) <= 0) # type (5) constraint

print("Creating objective function...", flush = True)
objectiveTerms = [] # list of terms that will be added together to make the objective function
# create type (1) terms
for var1 in varByType[1]:
	_, varMentor, varTeam = groupByVar[var1] # figure out which mentor and team this variable is for
	value = utils.getTeamCompatibility(varMentor, varTeam) - utils.getMentorAloneCost(varMentor)
	objectiveTerms.append(value * var1)
# create type (2) terms
for var2 in varByType[2]:
	_, varMentor, varTeam = groupByVar[var2] # figure out which mentor and team this variable is for
	value = utils.getTeamCompatibility(varMentor, varTeam)
	objectiveTerms.append(value * var2)
objective = sum(objectiveTerms)

print("Creating problem...", flush = True)
prob = cp.Problem(cp.Maximize(objective), constraints)

print("Solving problem...", flush = True)
startTime = time.time()
prob.solve()
endTime = time.time()

if prob.value is None:
	print("Something went wrong in the problem solving???")
	print("Problem status:", prob.status)
	print("Time elapsed:", endTime - startTime)
else:
	print("Problem solved!  Time elapsed: " + str(endTime - startTime) + "\n  Final objective value of " + str(prob.value))
	print("\n\nHere is the matching:")
	for variable in variables:
		if variable.value > 0.5:
			_, varMentor, varTeam = groupByVar[variable]
			print("Matched " + varMentor.name + " to " + varTeam.name)
