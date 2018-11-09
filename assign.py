"""USAGE: python3 assign.py <csv-file>

Here is a sample CSV file.

    Name,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,119,120,121,122,123
    Tina,3,1,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,2,2,0,0,0
    Michelle,2,2,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    Courtney,0,0,0,0,0,0,0,0,0,3,0,0,2,2,3,2,2,0,0,0,0,0
    Shreyas,0,0,2,3,0,0,1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0
    Nicole,0,0,0,0,0,0,0,0,0,2,0,0,1,1,2,3,0,0,0,0,0,0
    Yuxiang,0,0,0,0,0,0,0,0,0,2,1,0,0,0,0,2,3,2,2,1,0,0
    Ray,0,0,0,0,0,2,1,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0
    Harley,0,0,2,2,1,1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0
    Kaylee,1,1,1,1,2,2,0,0,0,1,0,2,0,0,0,0,0,2,3,0,0,0
    Jerry,2,2,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0
    Alex,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,2,2
    Isla,0,0,3,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    Isla,0,0,3,0,0,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    James,0,0,0,0,0,3,2,1,1,0,1,2,0,0,0,0,0,0,0,0,0,0
    Alvin,0,0,2,2,3,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    William,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,3,2,2,0,0,0
    Margaret,3,0,3,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    Margaret,3,0,3,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    Benjamin,1,2,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    Serena,0,0,0,0,0,0,1,1,1,0,2,0,3,2,2,0,0,1,1,0,0,0
    Cynthia,1,2,2,3,0,0,0,0,0,0,0,1,0,0,0,0,0,2,2,0,0,0
    Jonathan,2,2,0,0,0,0,0,0,0,2,0,0,0,0,0,2,2,2,3,2,0,0

The first row is a header containing the names of the sections. The other rows
are comma-separated lists of section preferences ranging from 0 to 3.

DESCRIPTION: assign.py formulates the assignment problem as a maximum weighted
bipartite matching problem, which has integer LP solutions.
"""


import csv
import cvxpy as cvx
import numpy as np
import sys


if __name__ == "__main__":
    with open(sys.argv[1], "r") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        sections = header[1:]
        constraints = []
        preferences = {}
        section_variables = [[] for section in sections]
        weights = []
        variables = []
        num_tas = 0
        for row in reader:
            name = row[0]
            num_tas += 1
            edges = []
            preferences[name] = {}
            for i in range(len(row) - 1):
                section = sections[i]
                preferences[name][section] = row[i + 1]
                weights.append(int(row[i + 1]))

                # Currently broken with cvxpy version 0.4.10.
                # See: https://github.com/cvxgrp/cvxpy/issues/364
                # Follow the instructions in the above thread (edit your
                # `site-packages`), or simply wait for a new version of cvxpy
                # and upgrade your cvxpy version.

                # The variables are indicator variables for whether a TA is
                # assigned to a particular section.
                variable = cvx.Bool(name="{}-{}".format(name, section))
                variables.append(variable)
                edges.append(variable)
                section_variables[i].append(variable)
            # Add constraint that each TA is assigned one section.
            edges = np.array(edges)
            constraints.append(sum(edges) == 1)
        # Add constraint that each section is assigned one TA.
        for section in section_variables:
            constraints.append(sum(section) == 1)
        weights = np.array(weights)
        variables = np.array(variables)
        objective = cvx.Maximize(weights.dot(variables))
        problem = cvx.Problem(objective, constraints)
        error_msg = "The number of TAs does not match the number of sections!"
        assert num_tas == len(sections), error_msg
        print("Objective Value:", problem.solve())
        for variable in variables:
            if variable.value >= 0.5:
                name, section = variable.name().split("-")
                choice = preferences[name][section]
                print("Assigned {} to {} (Choice {})".format(name, section, choice))

