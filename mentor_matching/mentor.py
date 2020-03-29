import csv
from typing import IO
from typing import List

from mentor_matching.constants import availableMark
from mentor_matching.constants import comfortAloneLevels
from mentor_matching.constants import mentorHeaderRows
from mentor_matching.constants import multiItemDelimiter
from mentor_matching.constants import numSkills
from mentor_matching.constants import numTeamTypes
from mentor_matching.constants import numTypesTransit
from mentor_matching.constants import skillConfidenceLevels
from mentor_matching.constants import slotsPerDay
from mentor_matching.constants import teamTypeNoMark
from mentor_matching.constants import teamTypeYesMark
from mentor_matching.constants import transit_convenience
from mentor_matching.constants import unavailableMark
from mentor_matching.team import ensure_in_set
from mentor_matching.team import parse_availability


class Mentor:
    """
    class representing a mentor
    stores information about a mentor from the spreadsheet and contains various helper functions specific to mentors
    attributes:
        name: the mentor's name as a string
        availability: the mentor's availability
                        each sublist corresponds to one day, and has a boolean value for each slot
        teamTypeRequests: the mentor's requests for team types
                            each entry corresponds to one team type
        teamsRequested: a list of the name(s) of team(s) a mentor has requested to be on (given extra weight)
                            the list is empty if no teams are requested
        teamsRequired: a list of the name(s) of team(s) a mentor must be assigned to one of
                            the list is empty if no teams are required
        mentorsRequired: a list of the name(s) of other mentor(s) a mentor must be paired with
                            the list is empty if no other mentors are required
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
        teams_required: List[str],
        mentors_required: List[str],
        comfort_alone: str,
        transit_conveniences: List[str],
        skills_confidence: List[str],
    ):
        self.name = name
        self.availability = availability
        self.teamTypeRequests = team_type_requests
        self.teamsRequested = teams_requested
        self.teamsRequired = teams_required
        self.mentorsRequired = mentors_required
        self.comfortAlone = comfort_alone
        self.transitConveniences = transit_conveniences
        self.skillsConfidence = skills_confidence

    @classmethod
    def from_list(cls, data_row):
        """
        Initialize a mentor from a spreadsheet row

        data_row should contain all the data about a mentor, formatted as described in the comments at the top of this file
            all entries should be strings (as is output by a csv reader), otherwise behavior is undefined
        will raise an exception if data is not formatted correctly
        """
        position = 0  # what position in data_row we are looking at right now

        # get name
        name = data_row[position]
        position += 1

        # get availabilities
        # this will be an array of arrays, where each subarray is the availability on a given day
        availability = parse_availability(
            data_row[position : position + sum(slotsPerDay)],
            slotsPerDay,
            availableMark,
            unavailableMark,
        )
        position += sum(slotsPerDay)

        # get team type requests
        teamTypeRequests = parse_team_type_requests(
            data_row[position : position + numTeamTypes],
            teamTypeYesMark,
            teamTypeNoMark,
        )
        position += numTeamTypes

        # get co-mentor / team requests and requirements
        teamsRequested = parse_multi_item_list(data_row[position], multiItemDelimiter)
        position += 1

        teamsRequired = parse_multi_item_list(data_row[position], multiItemDelimiter)
        position += 1

        mentorsRequired = parse_multi_item_list(data_row[position], multiItemDelimiter)
        position += 1

        comfort_alone_level = data_row[position]
        if comfort_alone_level not in comfortAloneLevels:
            raise ValueError(f"Got invalid comfort alone level {comfort_alone_level}")
        comfortAlone = comfort_alone_level
        position += 1

        # get transit type conveniences
        transitConveniences = ensure_in_set(
            data_row[position : position + numTypesTransit], transit_convenience,
        )
        position += numTypesTransit

        # get confidence in skills
        skillsConfidence = ensure_in_set(
            data_row[position : position + numSkills], skillConfidenceLevels
        )
        position += numSkills

        return cls(
            name,
            availability,
            teamTypeRequests,
            teamsRequested,
            teamsRequired,
            mentorsRequired,
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

    def mustPair(self, otherMentor) -> bool:
        """
        Returns whether or otherMentor appears in this mentor's list of mentors
        they are required to be matched with.
        """
        for name in self.mentorsRequired:
            if otherMentor.isMatch(name):
                return True
        return False


def mentors_from_file(mentors_file: IO[str]) -> List[Mentor]:
    mentors = []
    mentorReader = csv.reader(mentors_file)
    # remove header rows, if any
    for _ in range(mentorHeaderRows):
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
        if mark == teamTypeYesMark:
            return True
        elif mark == teamTypeNoMark:
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
