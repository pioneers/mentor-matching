import csv
from typing import IO
from typing import List

from mentor_matching import csv_parsing


class Team:
    """
    stores information about a team

    attributes:
        name: the team's name
        availability: the team's availability each sublist corresponds to
            one day, and has a boolean value for each slot
        team_types: whether the team falls into each team type
            each entry corresponds to one team type
        transit_times: how long each transit type would take in minutes
        skill_requests: how much the team wants each skill, as a list of elements from csv_parsing.skillRequestLevels
    """

    def __init__(
        self,
        name: str,
        availability: List[List[bool]],
        team_types: List[bool],
        transit_times: List[int],
        skill_requests: List[str],
    ):
        self.name = name
        self.availability = availability
        self.teamTypes = team_types
        self.transitTimes = transit_times
        self.skillRequests = skill_requests

    @classmethod
    def from_list(cls, dataRow: List[str]):
        """
        Initialize a team from a spreadsheet row

        dataRow should contain all the data about a team, formatted as described in the comments at the top of this file
        all entries should be strings (as is output by a csv reader), otherwise behavior is undefined

        will raise an exception if data is not formatted correctly
        """
        position = 0  # what position in dataRow we are looking at right now

        # get name
        name = dataRow[position]
        position += 1

        # get availabilities
        # this will be an array of arrays, where each subarray is the availability on a given day
        availability = csv_parsing.parse_availability(
            dataRow[position : position + sum(csv_parsing.slotsPerDay)],
            csv_parsing.slotsPerDay,
            csv_parsing.availableMark,
            csv_parsing.unavailableMark,
        )
        position += sum(csv_parsing.slotsPerDay)

        # get team types
        team_types = parse_team_type_data(
            dataRow[position : position + csv_parsing.numTeamTypes],
            csv_parsing.teamTypeYesMark,
            csv_parsing.teamTypeNoMark,
        )
        position += csv_parsing.numTeamTypes

        # get transit times
        transit_times = parse_transit_times(
            dataRow[position : position + csv_parsing.numTypesTransit]
        )
        position += csv_parsing.numTypesTransit

        # get requests for skills
        skill_requests = csv_parsing.ensure_in_set(
            dataRow[position : position + csv_parsing.numSkills],
            csv_parsing.skillRequestLevels,
        )
        position += csv_parsing.numSkills

        return cls(name, availability, team_types, transit_times, skill_requests)

    def isMatch(self, otherName):
        """
        Returns whether or not this team matches the input name
        Comparison ignores spaces and capitalization, but otherwise the names must match exactly
        """
        ownName = self.name.replace(" ", "").lower()
        otherName = otherName.replace(" ", "").lower()
        return ownName == otherName


def teams_from_file(teams_file: IO[str]) -> List[Team]:
    teams = []
    teamReader = csv.reader(teams_file)
    # remove header rows, if any
    for _ in range(csv_parsing.teamHeaderRows):
        next(teamReader)  # throw out header rows
    for dataRow in teamReader:
        teams.append(Team.from_list(dataRow))  # create the team object
    return teams


def parse_skill_requests(
    data: List[str], skill_request_levels: List[str],
) -> List[str]:
    def parse_skill_request(skill_request_level):
        if skill_request_level not in skill_request_levels:
            raise ValueError(
                f"Got invalid skill request level: {skill_request_level} in {data}"
            )
        return skill_request_level

    return [parse_skill_request(skill_request_level) for skill_request_level in data]


def parse_transit_times(data: List[str],) -> List[int]:
    def parse_transit_time(time: str) -> int:
        try:
            return int(time)
        except ValueError:
            raise ValueError(f"Got invalid transit time: {time} in {data}")

    return [parse_transit_time(transit_time) for transit_time in data]


def parse_team_type_data(data: List[str], yes_mark: str, no_mark: str,) -> List[bool]:
    def parse_team_type_mark(mark: str) -> bool:
        if mark == yes_mark:
            return True
        elif mark == no_mark:
            return False
        else:
            raise ValueError(f"Got invalid team type mark: {mark} in {data}")

    return [parse_team_type_mark(mark) for mark in data]
