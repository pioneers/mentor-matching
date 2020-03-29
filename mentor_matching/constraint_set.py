from typing import List

import cvxpy as cp

from mentor_matching.mentor import Mentor
from mentor_matching.objective_set import Parameters
from mentor_matching.team import Team
from mentor_matching.variable_set import VariableSet
from mentor_matching.variable_set import VariableType


class ConstraintSet(object):
    def __init__(
        self,
        var_set: VariableSet,
        mentors: List[Mentor],
        teams: List[Team],
        parameters: Parameters,
    ):
        self.constraints: List[cp.constraints.constraint.Constraint] = []

        self._var_set = var_set
        self._teams = teams
        self._mentors = mentors
        self._parameters = parameters

        self.ensure_assignment_types()
        self.ensure_one_mentor_per_team()
        self.ensure_mentor_number_constraints()
        self.ensure_mentor_pairings()

    def ensure_assignment_types(self) -> None:
        """
        Ensure that if only one mentor is assigned to the team, the program
        must use the corresponding SoloMentor variables, and not the
        GroupMentor variables.

        The sum of a team's type 2 variables plus twice the sum of its type 1
        variables must be at least 2.
        """
        for team in self._teams:
            typeOneVars = self._var_set.varByTeam[(VariableType.SoloMentor, team)]
            typeTwoVars = self._var_set.varByTeam[(VariableType.GroupMentor, team)]
            self.constraints.append(sum(typeTwoVars) + (2 * sum(typeOneVars)) >= 2)

    def ensure_one_mentor_per_team(self) -> None:
        """
        Ensure that a mentor gets matched with exactly one team.

        The sum of a mentor's type 1 and 2 variables is exactly 1.
        """
        for mentor in self._mentors:
            typeOneVars = self._var_set.varByMentor[(VariableType.SoloMentor, mentor)]
            typeTwoVars = self._var_set.varByMentor[(VariableType.GroupMentor, mentor)]
            self.constraints.append(sum(typeOneVars) + sum(typeTwoVars) == 1)

    def ensure_mentor_number_constraints(self):
        """
        Ensure that a team gets an appropriate number of mentors.

        The sum of a team's type 1 and 2 variables is between minNumMentors
        and maxNumMentors.
        """

        for team in self._teams:
            typeOneVars = self._var_set.varByTeam[(VariableType.SoloMentor, team)]
            typeTwoVars = self._var_set.varByTeam[(VariableType.GroupMentor, team)]
            self.constraints.append(
                sum(typeOneVars) + sum(typeTwoVars) >= self._parameters.minNumMentors
            )
            self.constraints.append(
                sum(typeOneVars) + sum(typeTwoVars) <= self._parameters.maxNumMentors
            )

    def ensure_mentor_pairings(self):
        """
        Ensure that mentors who are supposed to be paired together don't end
        up alone.

        For every pair of mentors who are required to be together, the sum of
        all their type 1 variables must be zero.

        Ensure that these mentors will be together, as if the second mentor is
        assigned to a team the first mentor isn't, that difference will be
        negative. This assumes these mentors aren't assigned using type 1
        variables, which the constraints of type 4 guarantee.

        For every pair of mentors who are required to be together and for each
        team, the difference between the type 2 variables for those mentors
        and that team must be greater than or equal to zero.
        """

        for mentor1 in self._mentors:
            for mentor2 in self._mentors:
                if self._mentors.index(mentor1) >= self._mentors.index(mentor2):
                    # we only want to consider each pair once, so ignore the second occurrence
                    # this also ensures that we don't consider pairing a mentor with themself
                    continue
                if mentor1.mustPair(mentor2) or mentor2.mustPair(mentor1):
                    # these mentors are required to be paired, so create the constraints for them
                    self.constraints.append(
                        (
                            sum(
                                self._var_set.varByMentor[
                                    (VariableType.SoloMentor, mentor1)
                                ]
                            )
                            + sum(
                                self._var_set.varByMentor[
                                    (VariableType.SoloMentor, mentor2)
                                ]
                            )
                            == 0
                        )
                    )  # type (4) constraint
                    for team in self._teams:
                        # get type (2) variables for these mentors and this team
                        mentor1Var = self._var_set.varByPair[
                            (VariableType.GroupMentor, mentor1, team)
                        ]
                        mentor2Var = self._var_set.varByPair[
                            (VariableType.GroupMentor, mentor2, team)
                        ]
                        self.constraints.append(
                            mentor1Var - mentor2Var >= 0
                        )  # type (5) constraint
