import csv
from typing import Any
from typing import Dict
from typing import IO
from typing import List

import yaml

from mentor_matching import csv_parsing
from mentor_matching.mentor import Mentor
from mentor_matching.team import Team


class Parameters(object):
    """
    Weights and other matching-related constants

    These parameters will affect how we match mentors with teams.

    We document what each of the parameters do in the example data as we
    expect people to read the documentation while modifying the parameters.
    """

    def __init__(
        self,
        minNumMentors: int,
        maxNumMentors: int,
        minMeetingTime: int,
        totalMeetingTime: int,
        teamOverlapValue: int,
        mentorOverlapValue: int,
        noOverlapCost: int,
        partialOverlapCost: int,
        teamTypeMatchValue: int,
        teamRequestedValue: int,
        teamRequiredValue: int,
        skillMatchValues: List[List[int]],
        comfortAloneCosts: List[int],
        required_mentor_teams: Dict[str, List[str]],
        required_mentor_mentors: Dict[str, List[str]],
    ):
        self.minNumMentors = minNumMentors
        self.maxNumMentors = maxNumMentors
        self.minMeetingTime = minMeetingTime
        self.totalMeetingTime = totalMeetingTime
        self.teamOverlapValue = teamOverlapValue
        self.mentorOverlapValue = mentorOverlapValue
        self.noOverlapCost = noOverlapCost
        self.partialOverlapCost = partialOverlapCost
        self.teamTypeMatchValue = teamTypeMatchValue
        self.teamRequestedValue = teamRequestedValue
        self.teamRequiredValue = teamRequiredValue
        self.skillMatchValues = skillMatchValues
        self.comfortAloneCosts = comfortAloneCosts
        self.required_mentor_teams = required_mentor_teams
        self.required_mentor_mentors = required_mentor_mentors

        self.validate()

    @classmethod
    def from_file(cls, file_name: str):
        """
        Create Parameters from the appropriate constructor.

        Currently supports CSV and YAML
        """
        if file_name.endswith(".csv"):
            with open(file_name, "r") as csv_file:
                return cls.from_csv(csv_file)
        elif file_name.endswith(".yaml"):
            with open(file_name, "r") as yaml_file:
                return cls.from_yaml(yaml_file)
        else:
            raise ValueError(f"Unsuported file type: {file_name}")

    @classmethod
    def from_csv(cls, parameters_file: IO[str]):
        """
        Create Parameters from a CSV.

        Blank lines or lines that begin with '#' are ignored.

        As show by the lengths of from_csv and from_yaml, parsing parameters
        is much simpler with the standard YAML format rather than defining a
        new one via CSV. We use CSV because CSV is the easily parseable
        version of Google Sheets, the collaboration tool of choice for ad-hoc
        UIs.
        """
        reader = csv.reader(parameters_file)

        fields: Dict[str, Any] = {}
        fields["required_mentor_teams"] = {}
        fields["required_mentor_mentors"] = {}

        for line in reader:
            # skip blank lines
            if len(line) == 0:
                continue

            # skip all commented lines
            key = line[0]
            if key.startswith("#"):
                continue

            vals = list(filter(lambda x: x != "", line[1:]))

            # skip blank lines
            if len(vals) == 0:
                continue

            if len(vals) == 1:
                fields[key] = int(vals[0])
            elif key == "skillMatchValues":
                num_skills = 5
                num_skill_vals = 5
                str_vals = [
                    list(
                        map(int, vals[i * num_skills : i * num_skills + num_skill_vals])
                    )
                    for i in range(num_skills)
                ]
                fields[key] = str_vals
            elif key == "comfortAloneCosts":
                fields[key] = list(map(int, vals))
            elif key == "required_mentor_teams":
                mentor = vals[0]
                teams = vals[1:]
                fields[key][mentor] = teams
            elif key == "required_mentor_mentors":
                mentor = vals[0]
                other_mentors = vals[1:]
                fields[key][mentor] = other_mentors
            else:
                raise ValueError(f"can't parse line: {line}")
        return cls(**fields)

    @classmethod
    def from_yaml(cls, parameters_file: IO[str]):
        """
        Creates Parameters from a file

        >>> with open("some_file.yaml") as f:
        >>>   parameters = Parameters.from_file(f)
        <Parameters object>
        """
        parsed_dict = yaml.load(parameters_file, Loader=yaml.Loader)
        return cls(**parsed_dict)

    def required_mentor_mentor(self, mentor_name: str, other_mentor_name: str):
        """
        Return if a mentor is required to mentor with another mentor.

        Performs a bi-directional check.
        """
        if other_mentor_name in self.required_mentor_mentors:
            if mentor_name in self.required_mentor_mentors[other_mentor_name]:
                return True
        if mentor_name in self.required_mentor_mentors:
            if other_mentor_name in self.required_mentor_mentors[mentor_name]:
                return True
        return False

    def required_mentor_team(self, mentor_name: str, team_name: str):
        """Return if a mentor is required to mentor for a team"""
        if mentor_name in self.required_mentor_teams:
            if team_name in self.required_mentor_teams[mentor_name]:
                return True
        return False

    def validate(self) -> None:
        """Ensure that parameters are valid and sane"""
        if self.minNumMentors > self.maxNumMentors:
            raise ValueError(
                f"minNumMenotrs ({self.minNumMentors} cannot be greater than maxNumMentors ({self.maxNumMentors})"
            )
        if len(self.comfortAloneCosts) != len(csv_parsing.comfortAloneLevels):
            raise ValueError(
                f"comfortAloneCosts ({self.comfortAloneCosts}) and comfortAloneLevels {csv_parsing.comfortAloneLevels} do not match length"
            )

    def validate_names(self, mentors: List[Mentor], teams: List[Team]) -> None:
        """Ensure that all mentor and team names are actual mentors/teams"""
        mentor_names = {mentor.name for mentor in mentors}
        team_names = {team.name for team in teams}

        illegal_mentor_names = []
        illegal_team_names = []

        def check_mentor_name(name: str) -> None:
            if name not in mentor_names:
                illegal_mentor_names.append(name)

        for mentor_name in self.required_mentor_mentors:
            check_mentor_name(mentor_name)
            for other_mentor_name in self.required_mentor_mentors[mentor_name]:
                check_mentor_name(other_mentor_name)

        def check_team_name(name: str) -> None:
            if name not in team_names:
                illegal_team_names.append(name)

        for mentor_name in self.required_mentor_teams:
            check_mentor_name(mentor_name)
            for team_name in self.required_mentor_teams[mentor_name]:
                check_team_name(team_name)

        if illegal_mentor_names or illegal_team_names:
            raise ValueError(
                f"Unable to find mentor names ({illegal_mentor_names}) and team names ({illegal_team_names})"
            )
