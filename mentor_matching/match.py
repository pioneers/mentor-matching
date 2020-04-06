import time
from typing import List
from typing import Optional

import cvxpy as cp

from mentor_matching.assignment_set import AssignmentSet
from mentor_matching.constraint_set import ConstraintSet
from mentor_matching.mentor import Mentor
from mentor_matching.objective_set import ObjectiveSet
from mentor_matching.objective_set import Parameters
from mentor_matching.team import Team


def match(
    mentors: List[Mentor], teams: List[Team], parameters: Parameters
) -> Optional[AssignmentSet]:
    """Assign each mentor to a team while optimizing"""
    print("Creating optimization variables...", flush=True)
    assignment_set = AssignmentSet(mentors, teams)

    print("Creating constraints...", flush=True)
    constraint_set = ConstraintSet(assignment_set, mentors, teams, parameters)

    print("Creating objective function...", flush=True)
    objective_set = ObjectiveSet(assignment_set, parameters)

    print("Creating problem...", flush=True)
    prob = cp.Problem(
        cp.Maximize(objective_set.objective()), constraint_set.constraints
    )

    print("Solving problem...", flush=True)
    start_time = time.time()
    prob.solve()
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"Time elapsed {elapsed_time:.2f}")

    if prob.value is None:
        print("Something went wrong in the problem solving???")
        print("Problem status:", prob.status)
        return None

    print("Problem solved!")
    print(f"Final objective value of {prob.value:.2f}")

    return assignment_set
