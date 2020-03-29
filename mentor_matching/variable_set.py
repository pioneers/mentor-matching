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


class VariableSet(object):
    """Contains all variable for the optimization"""

    def __init__(self, mentors: List[Mentor], teams: List[Team]):
        self._mentors = mentors
        self._teams = teams

        # list of all variables
        self.variables: List[cp.Variable] = []

        # map from variable type to list of variables of that type
        self.varByType: Dict[VariableType, List[cp.Variable]] = {}

        # map from (variable type, mentor) to list of variables of that type for that mentor
        self.varByMentor: Dict[Tuple[VariableType, Mentor], List[cp.Variable]] = {}

        # map from (variable type, team) to list of variables of that type for that team
        self.varByTeam: Dict[Tuple[VariableType, Team], List[cp.Variable]] = {}

        # map from (variable type, mentor, team) to list of variable of that type for that team and mentor
        self.varByPair: Dict[Tuple[VariableType, Mentor, Team], cp.Variable] = {}

        # map from a variable to the (variable type, mentor, team) corresponding to it
        self.groupByVar: Dict[cp.Variable, Tuple[VariableType, Mentor, Team]] = {}

        # initialize varByType, varByMentor, varByTeam, and varByPair with empty lists to prevent KeyErrors later
        for varType in VariableType:
            self.varByType[varType] = []
            for mentor in self._mentors:
                self.varByMentor[(varType, mentor)] = []
            for team in self._teams:
                self.varByTeam[(varType, team)] = []

        # create variables
        for varType in VariableType:
            for mentor in self._mentors:
                for team in self._teams:
                    # Each variable is tied to a mentor, team, and variable type.
                    # A value of 1 --> mentor is assigned to that team.
                    newVar = cp.Variable(boolean=True)
                    self.variables.append(newVar)
                    self.varByType[varType].append(newVar)
                    self.varByMentor[(varType, mentor)].append(newVar)
                    self.varByTeam[(varType, team)].append(newVar)
                    self.varByPair[(varType, mentor, team)] = newVar
                    self.groupByVar[newVar] = (varType, mentor, team)

    def mentors_by_team(self) -> Dict[Team, List[Mentor]]:
        """
        Return a map to see the mentors for a team.
        Return empty if the problem hasn't been solved.
        """
        mentors_by_team: Dict[Team, List[Mentor]] = {}
        for team in self._teams:
            mentors_by_team[team] = []
        for var in self.variables:
            if var.value > 0.5:
                _, mentor, team = self.groupByVar[var]
                mentors_by_team[team].append(mentor)
        return mentors_by_team

    def team_by_mentor(self) -> Dict[Mentor, Team]:
        """
        Return a map to team for a mentor.
        Return empty if the problem hasn't been solved.
        """
        team_by_mentor = {}
        for var in self.variables:
            if var.value > 0.5:
                _, mentor, team = self.groupByVar[var]
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


class VariableType(Enum):
    # SoloMentor variables indicate if a mentor is assigned to a team alone
    SoloMentor = auto()
    # GroupMentor variables indicate if a mentor is assigned to a team with
    # at least one other mentor
    GroupMentor = auto()
