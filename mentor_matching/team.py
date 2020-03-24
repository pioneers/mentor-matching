import csv
from typing import IO
from typing import List

from mentor_matching.constants import availableMark
from mentor_matching.constants import numSkills
from mentor_matching.constants import numTeamTypes
from mentor_matching.constants import numTypesTransit
from mentor_matching.constants import skillRequestLevels
from mentor_matching.constants import slotsPerDay
from mentor_matching.constants import teamHeaderRows
from mentor_matching.constants import teamTypeNoMark
from mentor_matching.constants import teamTypeYesMark
from mentor_matching.constants import unavailableMark


class Team:
    """
    class representing a team
    stores information about a team from the spreadsheet and contains various helper functions specific to teams
    attributes:
        name: the team's name as a string
        availability: the team's availability as a boolean matrix
                        each sublist corresponds to one day, and has a boolean value for each slot
        teamTypes: whether the team falls into each team type, as a boolean list
                            each entry corresponds to one team type
        transitTimes: how long each transit type would take in minutes, as a list integers
        skillRequests: how much the team wants each skill, as a list of elements from skillRequestLevels
    """

    def __init__(self, dataRow):
        """
        Initialize a team from a spreadsheet row
        dataRow should contain all the data about a team, formatted as described in the comments at the top of this file
            all entries should be strings (as is output by a csv reader), otherwise behavior is undefined
        will raise an exception if data is not formatted correctly
        """
        position = 0  # what position in dataRow we are looking at right now

        # get name
        self.name = dataRow[position]
        position += 1

        # get availabilities
        self.availability = (
            []
        )  # this will be an array of arrays, where each subarray is the availability on a given day
        for numSlots in slotsPerDay:
            dayAvailability = []
            for slot in range(numSlots):
                if dataRow[position] == availableMark:
                    dayAvailability.append(1)
                elif dataRow[position] == unavailableMark:
                    dayAvailability.append(0)
                else:
                    raise ValueError(
                        "Got invalid value "
                        + dataRow[position]
                        + " for "
                        + self.name
                        + "'s availability in column "
                        + str(position + 1)
                    )
                position += 1
            self.availability.append(dayAvailability)

        # get team types
        self.teamTypes = []
        for teamType in range(numTeamTypes):
            if dataRow[position] == teamTypeYesMark:
                self.teamTypes.append(1)
            elif dataRow[position] == teamTypeNoMark:
                self.teamTypes.append(0)
            else:
                raise ValueError(
                    "Got invalid value "
                    + dataRow[position]
                    + " for "
                    + self.name
                    + "'s team type in column "
                    + str(position + 1)
                )
            position += 1

        # get transit times
        self.transitTimes = []
        for transitType in range(numTypesTransit):
            try:
                self.transitTimes.append(
                    int(dataRow[position])
                )  # if dataRow[position] isn't an integer, this will raise a ValueError
                position += 1
            except ValueError:
                raise ValueError(
                    "Got invalid value "
                    + dataRow[position]
                    + " for "
                    + self.name
                    + "'s travel time in column "
                    + str(position + 1)
                )

        # get requests for skills
        self.skillRequests = []
        for skill in range(numSkills):
            if dataRow[position] not in skillRequestLevels:
                raise ValueError(
                    "Got invalid value "
                    + dataRow[position]
                    + " for "
                    + self.name
                    + "'s team skill request in column "
                    + str(position + 1)
                )
            self.skillRequests.append(dataRow[position])
            position += 1

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
    for _ in range(teamHeaderRows):
        next(teamReader)  # throw out header rows
    for dataRow in teamReader:
        teams.append(Team(dataRow))  # create the team object
    return teams
