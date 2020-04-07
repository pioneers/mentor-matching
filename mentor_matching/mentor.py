import csv
from typing import IO
from typing import List

from mentor_matching import csv_parsing


class Mentor:
    """
    Parses mentor information from a CSV row and provides organized access.

    attributes:
        name: the mentor's name as a string
        availability: the mentor's availability
                        each sublist corresponds to one day, and has a boolean value for each slot
        teamTypeRequests: the mentor's requests for team types
                            each entry corresponds to one team type
        teamsRequested: a list of the name(s) of team(s) a mentor has requested to be on (given extra weight)
                            the list is empty if no teams are requested
        comfortAlone: how comfortable the mentor is mentoring alone
        transitConveniences: how convenient each transit type is, as a list of keys from transit_convenience
        skillsConfidence: how confident the mentor is in each skill, as a list of elements from skillConfidenceLevels
    """

    def __init__(
        self,
        name: str,
        availability: List[List[bool]],
        team_type_requests: List[bool],
        teams_requested: List[str],
        comfort_alone: str,
        transit_conveniences: List[str],
        skills_confidence: List[str],
    ):
        self.name = name
        self.availability = availability
        self.teamTypeRequests = team_type_requests
        self.teamsRequested = teams_requested
        self.comfortAlone = comfort_alone
        self.transitConveniences = transit_conveniences
        self.skillsConfidence = skills_confidence

    @classmethod
    def from_list(cls, data_row):
        """
        Initialize a mentor from a spreadsheet row

        data_row should contain all the data about a mentor, formatted as
            described in the comments at the top of this file all entries
            should be strings (as is output by a csv reader), otherwise
            behavior is undefined.

        will raise an exception if data is not formatted correctly
        """
        position = 0  # what position in data_row we are looking at right now

        # get name
        name = data_row[position]
        position += 1

        # get availabilities
        # this will be an array of arrays, where each subarray is the availability on a given day
        availability = csv_parsing.parse_availability(
            data_row[position : position + sum(csv_parsing.slotsPerDay)],
            csv_parsing.slotsPerDay,
            csv_parsing.availableMark,
            csv_parsing.unavailableMark,
        )
        position += sum(csv_parsing.slotsPerDay)

        # get team type requests
        teamTypeRequests = parse_team_type_requests(
            data_row[position : position + csv_parsing.numTeamTypes],
            csv_parsing.teamTypeYesMark,
            csv_parsing.teamTypeNoMark,
        )
        position += csv_parsing.numTeamTypes

        # get co-mentor / team requests and requirements
        teamsRequested = parse_multi_item_list(
            data_row[position], csv_parsing.multiItemDelimiter
        )
        position += 1

        # skip teamsRequired
        position += 1

        # skip mentorsRequired
        position += 1

        comfort_alone_level = data_row[position]
        if comfort_alone_level not in csv_parsing.comfortAloneLevels:
            raise ValueError(f"Got invalid comfort alone level {comfort_alone_level}")
        comfortAlone = comfort_alone_level
        position += 1

        # get transit type conveniences
        transitConveniences = csv_parsing.ensure_in_set(
            data_row[position : position + csv_parsing.numTypesTransit],
            csv_parsing.transit_convenience,
        )
        position += csv_parsing.numTypesTransit

        # get confidence in skills
        skillsConfidence = csv_parsing.ensure_in_set(
            data_row[position : position + csv_parsing.numSkills],
            csv_parsing.skillConfidenceLevels,
        )
        position += csv_parsing.numSkills

        return cls(
            name,
            availability,
            teamTypeRequests,
            teamsRequested,
            comfortAlone,
            transitConveniences,
            skillsConfidence,
        )

    def isMatch(self, otherName: str) -> bool:
        """
        Returns whether or not this mentor matches the input name

        Comparison ignores spaces and capitalization, but otherwise the names
        must match exactly
        """
        ownName = self.name.replace(" ", "").lower()
        otherName = otherName.replace(" ", "").lower()
        return ownName == otherName


def mentors_from_file(mentors_file: IO[str]) -> List[Mentor]:
    mentors = []
    mentorReader = csv.reader(mentors_file)
    # remove header rows, if any
    for _ in range(csv_parsing.mentorHeaderRows):
        next(mentorReader)  # just read the row and throw it away
    for data_row in mentorReader:
        mentors.append(
            Mentor.from_list(data_row)
        )  # create a new mentor object based on each row of data
    return mentors


def parse_team_type_requests(
    data: List[str], yes_mark: str, no_mark: str,
) -> List[bool]:
    def parse_team_type_mark(mark: str) -> bool:
        if mark == csv_parsing.teamTypeYesMark:
            return True
        elif mark == csv_parsing.teamTypeNoMark:
            return False
        else:
            raise ValueError(f"Got invalid mark {mark} in {data}")

    return [parse_team_type_mark(mark) for mark in data]


def parse_multi_item_list(entry: str, multi_item_delimiter: str,) -> List[str]:
    """
    Split a string into elements and cleans them.

    >>> parse_multi_item_list("sure; next; great", ";")
    ["sure", "next", "great"]

    >>> parse_multi_item_list("", ";")
    []
    """
    if entry == "":
        return []

    return [name.strip() for name in entry.split(multi_item_delimiter)]
