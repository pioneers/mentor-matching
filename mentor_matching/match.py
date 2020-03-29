import time
from typing import List
from typing import Optional

import cvxpy as cp

from mentor_matching.constraint_set import ConstraintSet
from mentor_matching.mentor import Mentor
from mentor_matching.objective_set import ObjectiveSet
from mentor_matching.objective_set import Parameters
from mentor_matching.team import Team
from mentor_matching.variable_set import VariableSet


def match(
    mentors: List[Mentor], teams: List[Team], parameters: Parameters
) -> Optional[VariableSet]:
    """Assign each mentor to a team while optimizing"""
    print("Creating optimization variables...", flush=True)
    var_set = VariableSet(mentors, teams)

    print("Creating constraints...", flush=True)
    constraint_set = ConstraintSet(var_set, mentors, teams, parameters)

    print("Creating objective function...", flush=True)
    objective_set = ObjectiveSet(var_set, parameters)

    print("Creating problem...", flush=True)
    prob = cp.Problem(
        cp.Maximize(objective_set.objective()), constraint_set.constraints
    )

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
    return var_set
