"""
Main script for running mentor matching
"""

import cvxpy as cp
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
				teamNum = teams.index(team) # we will use this as the multiplier for this team
				mentor1Var = varByPair[(2, mentor1, team)][0] # get type (2) variables for these mentors and this team
				mentor2Var = varByPair[(2, mentor2, team)][0] # there will only be one variable in each list, so extract it
				diffTerms.append(teamNum * (mentor1Var - mentor2Var))
			constraints.append(sum(diffTerms) == 0) # type (5) constraint

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
