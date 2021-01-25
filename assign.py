"""
Main script for running mentor matching
"""

import utils
from utils import Mentor, Team
import csv
import sys

import time # for testing purposes

useGurobi = False # an indicator for whether to use Gurobi (or cvxpy) as the solver
# use -g in the command line to use Gurobi; otherwise will default to cvxpy
if "-g" in sys.argv:
	useGurobi = True

if useGurobi:
	import gurobipy as gp
else:
	import cvxpy as cp


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

print("Creating compatibility file...", flush = True)
with open('compatibility.csv', 'w', newline = '') as compatFile:
	compatWriter = csv.writer(compatFile)
	firstRow = ['Name'] # first row is a header that gives the name of each team
	for team in teams:
		firstRow.append(team.name)
	compatWriter.writerow(firstRow)
	for mentor in mentors:
		mentorRow = [mentor.name] # contains the name of this mentor + compatibility for each team
		for team in teams:
			mentorRow.append(str(utils.getTeamCompatibility(mentor, team)))
		compatWriter.writerow(mentorRow)
print("Compatibilities output to compatibility.csv")

if useGurobi:
	print("Initializing model...", flush = True)
	m = gp.Model()

print("Creating optimization variables...", flush = True)
variables = [] # list of all variables
varByType = {} # map from variable type to list of variables of that type
varByMentor = {} # map from (variable type, mentor) to list of variables of that type for that mentor
varByTeam = {} # map from (variable type, team) to list of variables of that type for that team
varByPair = {} # map from (variable type, mentor, team) to list of variable of that type for that team and mentor
groupByVar = {} # map from a variable to the (variable type, list of mentors, team) corresponding to it
# initialize varByType, varByMentor, varByTeam, and varByPair with empty lists to prevent KeyErrors later
for varType in [1, 2, 3, 4]:
	varByType[varType] = []
	for mentor in mentors:
		varByMentor[(varType, mentor)] = []
		for team in teams:
			varByPair[(varType, mentor, team)] = []
	for team in teams:
		varByTeam[(varType, team)] = []
# create variables of type 1 and 3 (one per mentor-team pair)
for varType in [1, 3]:
	for mentor in mentors:
		for team in teams:
			if useGurobi:
				newVar = m.addVar(vtype = gp.GRB.BINARY)
				m.update() # needed to ensure that the variable we just created can be used as a key in the groupByVar dictionary
			else:
				newVar = cp.Variable(boolean = True)
			variables.append(newVar)
			varByType[varType].append(newVar)
			varByMentor[(varType, mentor)].append(newVar)
			varByTeam[(varType, team)].append(newVar)
			varByPair[(varType, mentor, team)].append(newVar)
			groupByVar[newVar] = (varType, [mentor], team)
# create variables of type 2 (one per team)
for team in teams:
	if useGurobi:
		newVar = m.addVar(vtype = gp.GRB.BINARY)
		m.update() # needed to ensure that the variable we just created can be used as a key in the groupByVar dictionary
	else:
		newVar = cp.Variable(boolean = True)
	variables.append(newVar)
	varByType[2].append(newVar)
	varByTeam[(2, team)].append(newVar)
	groupByVar[newVar] = (2, [], team)
#create variables of type 4 (one per mentor-mentor-team group)
for mentor1 in mentors:
	for mentor2 in mentors:
		if mentor1.name >= mentor2.name:
			continue # only consider each pair once, don't consider groups where mentor1 and mentor2 are the same
		for team in teams:
			if useGurobi:
				newVar = m.addVar(vtype = gp.GRB.BINARY)
				m.update() # needed to ensure that the variable we just created can be used as a key in the groupByVar dictionary
			else:
				newVar = cp.Variable(boolean = True)
			variables.append(newVar)
			varByType[4].append(newVar)
			varByMentor[(4, mentor1)].append(newVar)
			varByMentor[(4, mentor2)].append(newVar)
			varByTeam[(4, team)].append(newVar)
			varByPair[(4, mentor1, team)].append(newVar)
			varByPair[(4, mentor2, team)].append(newVar)
			groupByVar[newVar] = (4, [mentor1, mentor2], team)

print("Creating constraints...", flush = True)
constraints = []
# create type 1 constraints
for mentor in mentors:
	typeOneVars = varByMentor[(1, mentor)]
	constraints.append(sum(typeOneVars) == 1)
# create type 2 constraints
for team in teams:
	typeOneVars = varByTeam[(1, team)]
	constraints.append(sum(typeOneVars) >= utils.minNumMentors)
	constraints.append(sum(typeOneVars) <= utils.maxNumMentors)
# create type 3 and 4 constraints
M = len(mentors)
for team in teams:
	typeTwoVar = varByTeam[(2, team)][0] # will only have a single variable in the list, so extract it
	typeOneVars = varByTeam[(1, team)]
	constraints.append(M * typeTwoVar <= M + 1 - sum(typeOneVars)) # type 3
	constraints.append(typeTwoVar >= 2 - sum(typeOneVars)) # type 4
# create type 5 constraints
for team in teams:
	typeTwoVar = varByTeam[(2, team)][0] # will only have a single variable in the list, so extract it
	typeThreeVars = varByTeam[(3, team)]
	constraints.append(sum(typeThreeVars) == typeTwoVar)
# create type 6 constraints
for mentor in mentors:
	for team in teams:
		typeOneVar = varByPair[(1, mentor, team)][0] # will only have a single variable in the list, so extract it
		typeThreeVar = varByPair[(3, mentor, team)][0] # ditto
		constraints.append(typeThreeVar <= typeOneVar)
# create type 7 constraints
M = len(mentors)
for mentor in mentors:
	for team in teams:
		typeOneVar = varByPair[(1, mentor, team)][0] # will only have a single variable in the list, so extract it
		typeFourVars = varByPair[(4, mentor, team)]
		constraints.append(sum(typeFourVars) <= M * typeOneVar)

print("Creating objective function...", flush = True)
objectiveTerms = [] # list of terms that will be added together to make the objective function
# create type 1 terms
for var1 in varByType[1]:
	_, varMentors, varTeam = groupByVar[var1] # figure out which mentor and team this variable is for
	varMentor = varMentors[0] # list will only have one mentor in it
	value = utils.getTeamCompatibility(varMentor, varTeam)
	objectiveTerms.append(value * var1)
# create type 2 terms
for var3 in varByType[3]:
	_, varMentors, varTeam = groupByVar[var3] # figure out which mentor and team this variable is for
	varMentor = varMentors[0] # list will only have one mentor in it
	value = utils.getAloneCompatibility(varMentor, varTeam)
	objectiveTerms.append(value * var3)
# create type 3 terms
for var4 in varByType[4]:
	_, varMentors, varTeam = groupByVar[var4] # figure out which mentor and team this variable is for
	value = utils.getGroupCompatibility(varMentors[0], varMentors[1], varTeam)
	objectiveTerms.append(value * var4)
# create type 4 term
numMentorReqs = 0 # how many pairs of mentors are required to be paired
for mentor1 in mentors:
	for mentor2 in mentors:
		if mentor1.name >= mentor2.name:
			continue # only consider each pair once, don't consider a mentor with themselves
		if mentor1.mustPair(mentor2) or mentor2.mustPair(mentor1):
			numMentorReqs += 1
numTeamReqs = 0 # how many mentors must be paired with a team
for mentor in mentors:
	for team in teams:
		if team.mustAssign(mentor):
			numTeamReqs += 1
			break # make sure we don't count this mentor twice if they have multiple required teams
offset = (numMentorReqs * utils.mentorRequiredValue) + (numTeamReqs * utils.teamRequiredValue)
objective = sum(objectiveTerms) - offset

print("Creating problem...", flush = True)
if useGurobi:
	for constraint in constraints:
		m.addConstr(constraint)
	m.setObjective(objective, gp.GRB.MAXIMIZE)
else:
	prob = cp.Problem(cp.Maximize(objective), constraints)

print("Solving problem...", flush = True)
startTime = time.time()
if useGurobi:
	m.optimize()
else:
	prob.solve()
endTime = time.time()


if useGurobi and m.Status not in [gp.GRB.Status.OPTIMAL, gp.GRB.Status.INTERRUPTED]:
	# something went wrong with the Gurobi solver
	print("Something went wrong in the problem solving???")
	possStatuses = ["N/A", "Not Yet Solved", "Optimum Found", "Infeasible", "Infeasible or Unbounded", "Unbounded", "Optimum Worse Than Cutoff",
						"Iteration Limit Reached", "Node Limit Reached", "Time Limit Reached", "Solution Limit Reached", "Interrupted",
						"Numerical Instability", "Suboptimal Solution", "Something About Asynchronus Stuff", "Objective Limit Reached"]
	print("Problem status:", possStatuses[m.Status])
	print("Time elapsed:", endTime - startTime)
elif (not useGurobi) and prob.value is None:
	# something went wrong with the cvxpy solver
	print("Something went wrong in the problem solving???")
	print("Problem status:", prob.status)
	print("Time elapsed:", endTime - startTime)
else:
	# whichever solver we used succeeded
	if useGurobi:
		value = m.objVal
	else:
		value = prob.value
	print("Problem solved!  Time elapsed: " + str(endTime - startTime) + "\nFinal objective value of " + str(value))
	teamByMentor = {} # mapping from a mentor to the team they are assigned to
	mentorsByTeam = {} # mapping from a team to a list of mentors assigned to that team
	for team in teams:
		mentorsByTeam[team] = [] # initialize all of these to empty lists so we can use append freely
	for variable in varByType[1]:
		if (useGurobi and variable.x > 0.5) or (not useGurobi and variable.value > 0.5):
			_, varMentors, varTeam = groupByVar[variable]
			varMentor = varMentors[0] # there will only be one mentor in this list, so extract it
			teamByMentor[varMentor] = varTeam
			mentorsByTeam[varTeam].append(varMentor)
	with open('matching.csv', 'w', newline = '') as matchFile:
		matchWriter = csv.writer(matchFile)
		matchWriter.writerow(['Mentor Name', 'Team Name', 'Other Mentor(s)'])
		for mentor in mentors:
			team = teamByMentor[mentor]
			otherMentors = mentorsByTeam[team][:] # make sure this is a copy and not a pointer to the original
			otherMentors.remove(mentor) 		  # otherwise this line will cause problems
			otherMentorsString = "" # will contain all the other mentors assigned to this team, separated by semicolons
			if len(otherMentors) == 0:
				otherMentorsString = "N/A"
			else:
				otherMentorsString = otherMentors[0].name
				for omIndex in range(1, len(otherMentors)):
					otherMentorsString += "; " + otherMentors[omIndex].name
			matchWriter.writerow([mentor.name, team.name, otherMentorsString])
	print("Matching output to matching.csv")
