import logging
import time
from typing import List
from typing import Optional

import cvxpy as cp

from mentor_matching.assignment_set import AssignmentSet
from mentor_matching.constraint_set import ConstraintSet
from mentor_matching.mentor import Mentor
from mentor_matching.objective_set import ObjectiveSet
from mentor_matching.parameters import Parameters
from mentor_matching.team import Team

logger = logging.getLogger(__name__)


def match(
    mentors: List[Mentor], teams: List[Team], parameters: Parameters
) -> Optional[AssignmentSet]:
    """Assign each mentor to a team while optimizing"""
    logger.info("Creating optimization variables...")
    assignment_set = AssignmentSet(mentors, teams)

    logger.info("Creating constraints...")
    constraint_set = ConstraintSet(assignment_set, mentors, teams, parameters)

    logger.info("Creating objective function...")
    objective_set = ObjectiveSet(assignment_set, parameters)

    logger.info("Creating problem...")
    prob = cp.Problem(
        cp.Maximize(objective_set.objective()), constraint_set.constraints
    )

    logger.info("Solving problem...")
    start_time = time.time()
    prob.solve()
    end_time = time.time()

    elapsed_time = end_time - start_time
    logger.info(f"Time elapsed {elapsed_time:.2f}")

    if prob.value is None:
        logger.error(
            "Something went wrong in the problem solving??? The required constraints may not have a valid solution. If you suspect this is the case, try adding the constraints one by one."
        )
        logger.error("Problem status:", prob.status)
        return None

    logger.info("Problem solved!")
    logger.info(f"Final objective value of {prob.value:.2f}")

    return assignment_set
