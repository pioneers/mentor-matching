import csv
from enum import auto
from enum import Enum
from typing import Dict
from typing import IO
from typing import List
from typing import Tuple

import cvxpy as cp

from mentor_matching.mentor import Mentor
from mentor_matching.team import Team


class AssignmentSet(object):
    """
    Contains all variables for the optimization.

    Each variable indicates whether a specific mentor is assigned to a
    specific school alone or with other mentors.
    """

    def __init__(self, mentors: List[Mentor], teams: List[Team]):
        self._mentors = mentors
        self._teams = teams

        # list of all variables
        self.assignments: List[cp.Variable] = []

        # map from variable type to list of variables of that type
        self.by_type: Dict[AssignmentType, List[cp.Variable]] = {}

        # map from (variable type, mentor) to list of variables of that type for that mentor
        self.by_mentor: Dict[Tuple[AssignmentType, Mentor], List[cp.Variable]] = {}

        # map from (variable type, team) to list of variables of that type for that team
        self.by_team: Dict[Tuple[AssignmentType, Team], List[cp.Variable]] = {}

        # map from (variable type, mentor, team) to list of variable of that type for that team and mentor
        self.by_mentor_team: Dict[Tuple[AssignmentType, Mentor, Team], cp.Variable] = {}

        # map from a variable to the (variable type, mentor, team) corresponding to it
        self.assignment_group: Dict[
            cp.Variable, Tuple[AssignmentType, Mentor, Team]
        ] = {}

        # initialize by_type, by_mentor, by_team, and by_mentor_team with empty lists to prevent KeyErrors later
        for assignment_type in AssignmentType:
            self.by_type[assignment_type] = []
            for mentor in self._mentors:
                self.by_mentor[(assignment_type, mentor)] = []
            for team in self._teams:
                self.by_team[(assignment_type, team)] = []

        # create variables
        for assignment_type in AssignmentType:
            for mentor in self._mentors:
                for team in self._teams:
                    # Each variable is tied to a mentor, team, and variable type.
                    # A value of 1 --> mentor is assigned to that team.
                    assignment = cp.Variable(boolean=True)
                    self.assignments.append(assignment)
                    self.by_type[assignment_type].append(assignment)
                    self.by_mentor[(assignment_type, mentor)].append(assignment)
                    self.by_team[(assignment_type, team)].append(assignment)
                    self.by_mentor_team[(assignment_type, mentor, team)] = assignment
                    self.assignment_group[assignment] = (assignment_type, mentor, team)

    def mentors_by_team(self) -> Dict[Team, List[Mentor]]:
        """
        Return a map to see the mentors for a team.
        Return empty if the problem hasn't been solved.
        """
        mentors_by_team: Dict[Team, List[Mentor]] = {}
        for team in self._teams:
            mentors_by_team[team] = []
        for assignment in self.assignments:
            if assignment.value > 0.5:
                _, mentor, team = self.assignment_group[assignment]
                mentors_by_team[team].append(mentor)
        return mentors_by_team

    def team_by_mentor(self) -> Dict[Mentor, Team]:
        """
        Return a map to team for a mentor.
        Return empty if the problem hasn't been solved.
        """
        team_by_mentor = {}
        for assignment in self.assignments:
            if assignment.value > 0.5:
                _, mentor, team = self.assignment_group[assignment]
                team_by_mentor[mentor] = team
        return team_by_mentor

    def write_match(self, match_file: IO[str]) -> None:
        """
        Write the matching to a file.
        Organizes by mentor -> team
        """
        match_writer = csv.writer(match_file)
        match_writer.writerow(["Mentor Name", "Team Name", "Other Mentor(s)"])

        teams_by_mentor = self.team_by_mentor()
        mentors_by_team = self.mentors_by_team()

        for mentor in self._mentors:
            team = teams_by_mentor[mentor]
            # make sure this is a copy and not a pointer to the original
            # otherwise this line will cause problems
            other_mentors = mentors_by_team[team][:]
            other_mentors.remove(mentor)
            other_mentors_string = ";".join([mentor.name for mentor in other_mentors])
            match_writer.writerow(
                [
                    mentor.name,
                    team.name,
                    other_mentors_string if other_mentors_string else "N/A",
                ]
            )


class AssignmentType(Enum):
    # SoloMentor assignments indicate if a mentor is assigned to a team alone
    SoloMentor = auto()
    # GroupMentor assignments indicate if a mentor is assigned to a team with
    # at least one other mentor
    GroupMentor = auto()
