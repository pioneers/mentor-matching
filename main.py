"""
Main script for running mentor matching
"""
import csv
import time  # for testing purposes

import cvxpy as cp
from utils import Mentor
from utils import Team

from mentor_matching import utils


print("Process started!  Reading mentor file...", flush=True)
mentors = []
with open("data/mentors-example.csv") as mentorFile:
    mentorReader = csv.reader(mentorFile)
    # remove header rows, if any
    for _ in range(utils.mentorHeaderRows):
        next(mentorReader)  # just read the row and throw it away
    for dataRow in mentorReader:
        mentors.append(
            Mentor(dataRow)
        )  # create a new mentor object based on each row of data

print("Reading team file...", flush=True)
teams = []
with open("data/teams-example.csv") as teamFile:
    teamReader = csv.reader(teamFile)
    # remove header rows, if any
    for _ in range(utils.teamHeaderRows):
        next(teamReader)  # throw out header rows
    for dataRow in teamReader:
        teams.append(Team(dataRow))  # create the team object

print("Creating compatibility file...", flush=True)
with open("compatibility.csv", "w", newline="") as compatFile:
    compatWriter = csv.writer(compatFile)
    firstRow = ["Name"]  # first row is a header that gives the name of each team
    for team in teams:
        firstRow.append(team.name)
    compatWriter.writerow(firstRow)
    for mentor in mentors:
        mentorRow = [
            mentor.name
        ]  # contains the name of this mentor + compatibility for each team
        for team in teams:
            mentorRow.append(str(utils.getTeamCompatibility(mentor, team)))
        compatWriter.writerow(mentorRow)
print("Compatibilities output to compatibility.csv")

print("Creating optimization variables...", flush=True)
variables = []  # list of all variables
varByType = {}  # map from variable type to list of variables of that type
varByMentor = (
    {}
)  # map from (variable type, mentor) to list of variables of that type for that mentor
varByTeam = (
    {}
)  # map from (variable type, team) to list of variables of that type for that team
varByPair = (
    {}
)  # map from (variable type, mentor, team) to list of variable of that type for that team and mentor
groupByVar = (
    {}
)  # map from a variable to the (variable type, mentor, team) corresponding to it
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
            newVar = cp.Variable(boolean=True)
            variables.append(newVar)
            varByType[varType].append(newVar)
            varByMentor[(varType, mentor)].append(newVar)
            varByTeam[(varType, team)].append(newVar)
            varByPair[(varType, mentor, team)].append(newVar)
            groupByVar[newVar] = (varType, mentor, team)

print("Creating constraints...", flush=True)
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
            constraints.append(
                sum(varByMentor[(1, mentor1)]) + sum(varByMentor[(1, mentor2)]) == 0
            )  # type (4) constraint
            for team in teams:
                mentor1Var = varByPair[(2, mentor1, team)][
                    0
                ]  # get type (2) variables for these mentors and this team
                mentor2Var = varByPair[(2, mentor2, team)][
                    0
                ]  # there will only be one variable in each list, so extract it
                constraints.append(mentor1Var - mentor2Var >= 0)  # type (5) constraint

print("Creating objective function...", flush=True)
objectiveTerms = (
    []
)  # list of terms that will be added together to make the objective function
# create type (1) terms
for var1 in varByType[1]:
    _, varMentor, varTeam = groupByVar[
        var1
    ]  # figure out which mentor and team this variable is for
    value = utils.getTeamCompatibility(varMentor, varTeam) - utils.getMentorAloneCost(
        varMentor
    )
    objectiveTerms.append(value * var1)
# create type (2) terms
for var2 in varByType[2]:
    _, varMentor, varTeam = groupByVar[
        var2
    ]  # figure out which mentor and team this variable is for
    value = utils.getTeamCompatibility(varMentor, varTeam)
    objectiveTerms.append(value * var2)
objective = sum(objectiveTerms)

print("Creating problem...", flush=True)
prob = cp.Problem(cp.Maximize(objective), constraints)

print("Solving problem...", flush=True)
startTime = time.time()
prob.solve()
endTime = time.time()

if prob.value is None:
    print("Something went wrong in the problem solving???")
    print("Problem status:", prob.status)
    print("Time elapsed:", endTime - startTime)
else:
    print(
        "Problem solved!  Time elapsed: "
        + str(endTime - startTime)
        + "\nFinal objective value of "
        + str(prob.value)
    )
    teamByMentor = {}  # mapping from a mentor to the team they are assigned to
    mentorsByTeam = {}  # mapping from a team to a list of mentors assigned to that team
    for team in teams:
        mentorsByTeam[
            team
        ] = []  # initialize all of these to empty lists so we can use append freely
    for variable in variables:
        if variable.value > 0.5:
            _, varMentor, varTeam = groupByVar[variable]
            teamByMentor[varMentor] = varTeam
            mentorsByTeam[varTeam].append(varMentor)
    with open("matching.csv", "w", newline="") as matchFile:
        matchWriter = csv.writer(matchFile)
        matchWriter.writerow(["Mentor Name", "Team Name", "Other Mentor(s)"])
        for mentor in mentors:
            team = teamByMentor[mentor]
            otherMentors = mentorsByTeam[team][
                :
            ]  # make sure this is a copy and not a pointer to the original
            otherMentors.remove(mentor)  # otherwise this line will cause problems
            otherMentorsString = ""  # will contain all the other mentors assigned to this team, separated by semicolons
            if len(otherMentors) == 0:
                otherMentorsString = "N/A"
            else:
                otherMentorsString = otherMentors[0].name
                for omIndex in range(1, len(otherMentors)):
                    otherMentorsString += "; " + otherMentors[omIndex].name
            matchWriter.writerow([mentor.name, team.name, otherMentorsString])
    print("Matching output to matching.csv")
