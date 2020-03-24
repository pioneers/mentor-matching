from typing import List

import cvxpy as cv

from mentor_matching.utils import getTeamCompatibility
from mentor_matching.variable_set import VariableSet
from mentor_matching.variable_set import VariableType


class ObjectiveSet(object):
    def __init__(
        self, var_set: VariableSet,
    ):
        self._var_set = var_set
        # list of terms that will be added together to make the objective function
        self._objective_terms: List[cv.expressions.expression.Expression] = []
        self._create_solo_mentor_terms()
        self._create_group_mentor_terms()

    def _create_solo_mentor_terms(self) -> None:
        for var in self._var_set.varByType[VariableType.SoloMentor]:
            _, mentor, team = self._var_set.groupByVar[var]
            value = getTeamCompatibility(mentor, team) - mentor.get_mentor_alone_cost()
            self._objective_terms.append(value * var)

    def _create_group_mentor_terms(self) -> None:
        for var in self._var_set.varByType[VariableType.GroupMentor]:
            # figure out which mentor and team this variable is for
            _, mentor, team = self._var_set.groupByVar[var]
            value = getTeamCompatibility(mentor, team)
            self._objective_terms.append(value * var)

    def objective(self):
        return sum(self._objective_terms)
