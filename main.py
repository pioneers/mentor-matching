"""
Main script for running mentor matching
"""
import csv
import time  # for testing purposes

import cvxpy as cp

from mentor_matching import utils
from mentor_matching.constraint_set import ConstraintSet
from mentor_matching.utils import create_team_compatability_data_frame
from mentor_matching.utils import mentors_from_file
from mentor_matching.utils import teams_from_file
from mentor_matching.variable_set import VariableSet
from mentor_matching.variable_set import VariableType


def main():
    print("Process started!  Reading mentor file...", flush=True)
    with open("data/mentors-example.csv") as mentorFile:
        mentors = mentors_from_file(mentorFile)

    print("Reading team file...", flush=True)
    with open("data/teams-example.csv") as team_file:
        teams = teams_from_file(team_file)

    print("Creating compatibility file...", flush=True)
    compatability_data_frame = create_team_compatability_data_frame(mentors, teams)
    compatability_data_frame.to_csv("compatability.csv")
    print("Compatibilities output to compatibility.csv")

    print("Creating optimization variables...", flush=True)
    var_set = VariableSet(mentors, teams)

    print("Creating constraints...", flush=True)
    constraint_set = ConstraintSet(var_set, mentors, teams,)

    print("Creating objective function...", flush=True)
    objectiveTerms = (
        []
    )  # list of terms that will be added together to make the objective function
    # create type (1) terms
    for var1 in var_set.varByType[VariableType.SoloMentor]:
        _, varMentor, varTeam = var_set.groupByVar[
            var1
        ]  # figure out which mentor and team this variable is for
        value = utils.getTeamCompatibility(
            varMentor, varTeam
        ) - utils.getMentorAloneCost(varMentor)
        objectiveTerms.append(value * var1)
    # create type (2) terms
    for var2 in var_set.varByType[VariableType.GroupMentor]:
        _, varMentor, varTeam = var_set.groupByVar[
            var2
        ]  # figure out which mentor and team this variable is for
        value = utils.getTeamCompatibility(varMentor, varTeam)
        objectiveTerms.append(value * var2)
    objective = sum(objectiveTerms)

    print("Creating problem...", flush=True)
    prob = cp.Problem(cp.Maximize(objective), constraint_set.constraints)

    print("Solving problem...", flush=True)
    startTime = time.time()
    prob.solve()
    endTime = time.time()

    if prob.value is None:
        print("Something went wrong in the problem solving???")
        print("Problem status:", prob.status)
        print("Time elapsed:", endTime - startTime)
        return None

    print(
        "Problem solved!  Time elapsed: "
        + str(endTime - startTime)
        + "\nFinal objective value of "
        + str(prob.value)
    )

    with open("matching.csv", "w", newline="") as match_file:
        var_set.write_match(match_file)
    print("Matching output to matching.csv")
    return var_set.team_by_mentor()


if __name__ == "__main__":
    main()
