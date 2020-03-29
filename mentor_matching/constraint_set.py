from typing import List

import cvxpy as cp

from mentor_matching.assignment_set import AssignmentSet
from mentor_matching.assignment_set import AssignmentType
from mentor_matching.mentor import Mentor
from mentor_matching.objective_set import Parameters
from mentor_matching.team import Team


class ConstraintSet(object):
    """Assembles all constraints for a valid matching"""

    def __init__(
        self,
        assignment_set: AssignmentSet,
        mentors: List[Mentor],
        teams: List[Team],
        parameters: Parameters,
    ):
        self.constraints: List[cp.constraints.constraint.Constraint] = []

        self._assignment_set = assignment_set
        self._teams = teams
        self._mentors = mentors
        self._parameters = parameters

        self.ensure_assignment_types()
        self.ensure_one_team_per_mentor()
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
            solo_assignments_for_team = self._assignment_set.by_team[
                (AssignmentType.SoloMentor, team)
            ]
            group_assignments_for_team = self._assignment_set.by_team[
                (AssignmentType.GroupMentor, team)
            ]
            self.constraints.append(
                sum(group_assignments_for_team) + (2 * sum(solo_assignments_for_team))
                >= 2
            )

    def ensure_one_team_per_mentor(self) -> None:
        """
        Ensure that a mentor gets matched with exactly one team.

        The sum of a mentor's type 1 and 2 variables is exactly 1.
        """
        for mentor in self._mentors:
            solo_assignments_for_mentor = self._assignment_set.by_mentor[
                (AssignmentType.SoloMentor, mentor)
            ]
            group_assignments_for_mentor = self._assignment_set.by_mentor[
                (AssignmentType.GroupMentor, mentor)
            ]
            self.constraints.append(
                sum(solo_assignments_for_mentor) + sum(group_assignments_for_mentor)
                == 1
            )

    def ensure_mentor_number_constraints(self):
        """
        Ensure that a team gets an appropriate number of mentors.

        The sum of a team's type 1 and 2 variables is between minNumMentors
        and maxNumMentors.
        """

        for team in self._teams:
            solo_assignments_for_team = self._assignment_set.by_team[
                (AssignmentType.SoloMentor, team)
            ]
            group_assignments_for_team = self._assignment_set.by_team[
                (AssignmentType.GroupMentor, team)
            ]
            self.constraints.append(
                sum(solo_assignments_for_team) + sum(group_assignments_for_team)
                >= self._parameters.minNumMentors
            )
            self.constraints.append(
                sum(solo_assignments_for_team) + sum(group_assignments_for_team)
                <= self._parameters.maxNumMentors
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

        for mentor_1 in self._mentors:
            for mentor_2 in self._mentors:
                if self._mentors.index(mentor_1) >= self._mentors.index(mentor_2):
                    # we only want to consider each pair once, so ignore the second occurrence
                    # this also ensures that we don't consider pairing a mentor with themself
                    continue
                if mentor_1.mustPair(mentor_2) or mentor_2.mustPair(mentor_1):
                    # these mentors are required to be paired, so create the constraints for them
                    # type (4) constraint
                    self.constraints.append(
                        (
                            sum(
                                self._assignment_set.by_mentor[
                                    (AssignmentType.SoloMentor, mentor_1)
                                ]
                            )
                            + sum(
                                self._assignment_set.by_mentor[
                                    (AssignmentType.SoloMentor, mentor_2)
                                ]
                            )
                            == 0
                        )
                    )
                    for team in self._teams:
                        # get type (2) variables for these mentors and this team
                        # type (5) constraint
                        mentor_1_assignment = self._assignment_set.by_mentor_team[
                            (AssignmentType.GroupMentor, mentor_1, team)
                        ]
                        mentor_2_assignment = self._assignment_set.by_mentor_team[
                            (AssignmentType.GroupMentor, mentor_2, team)
                        ]
                        self.constraints.append(
                            mentor_1_assignment - mentor_2_assignment >= 0
                        )
