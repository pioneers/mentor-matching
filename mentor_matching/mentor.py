import csv
from typing import IO
from typing import List

from mentor_matching.constants import aloneComfortLevels
from mentor_matching.constants import availableMark
from mentor_matching.constants import mentorHeaderRows
from mentor_matching.constants import multiItemDelimiter
from mentor_matching.constants import numSkills
from mentor_matching.constants import numTeamTypes
from mentor_matching.constants import numTypesTransit
from mentor_matching.constants import skillConfidenceLevels
from mentor_matching.constants import slotsPerDay
from mentor_matching.constants import teamTypeNoMark
from mentor_matching.constants import teamTypeYesMark
from mentor_matching.constants import transitConvenienceLevels
from mentor_matching.constants import unavailableMark


class Mentor:
    """
    class representing a mentor
    stores information about a mentor from the spreadsheet and contains various helper functions specific to mentors
    attributes:
        name: the mentor's name as a string
        availability: the mentor's availability as a boolean matrix
                        each sublist corresponds to one day, and has a boolean value for each slot
        teamTypeRequests: the mentor's requests for team types, as a boolean list
                            each entry corresponds to one team type
        teamsRequested: a list of the name(s) of team(s) a mentor has requested to be on (given extra weight)
                            the list is empty if no teams are requested
        teamsRequired: a list of the name(s) of team(s) a mentor must be assigned to one of
                            the list is empty if no teams are required
        mentorsRequired: a list of the name(s) of other mentor(s) a mentor must be paired with
                            the list is empty if no other mentors are required
        comfortAlone: how comfortable the mentor is mentoring alone, as an element from aloneComfortLevels
        transitConveniences: how convenient each transit type is, as a list of elements from transitConvenienceLevels
        skillsConfidence: how confident the mentor is in each skill, as a list of elements from skillConfidenceLevels
    """

    def __init__(self, dataRow):
        """
        Initialize a mentor from a spreadsheet row
        dataRow should contain all the data about a mentor, formatted as described in the comments at the top of this file
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
                        f"Got invalid value {dataRow[position]} for {self.name}'s availability in column {position + 1}"
                    )
                position += 1
            self.availability.append(dayAvailability)

        # get team type requests
        self.teamTypeRequests = []
        for teamType in range(numTeamTypes):
            if dataRow[position] == teamTypeYesMark:
                self.teamTypeRequests.append(1)
            elif dataRow[position] == teamTypeNoMark:
                self.teamTypeRequests.append(0)
            else:
                raise ValueError(
                    "Got invalid value "
                    + dataRow[position]
                    + " for "
                    + self.name
                    + "'s team type request in column "
                    + str(position + 1)
                )
            position += 1

        # get co-mentor / team requests and requirements
        self.teamsRequested = []
        if dataRow[position] != "":  # means the mentor requested at least one team
            # split up multiple team names, strip leading / trailing white space, and put into an array
            self.teamsRequested = [
                name.strip() for name in dataRow[position].split(multiItemDelimiter)
            ]
        position += 1
        self.teamsRequired = []
        if dataRow[position] != "":  # means the mentor is required by at least one team
            # split up multiple team names, strip leading / trailing white space, and put into an array
            self.teamsRequired = [
                name.strip() for name in dataRow[position].split(multiItemDelimiter)
            ]
        position += 1
        self.mentorsRequired = []
        if (
            dataRow[position] != ""
        ):  # means the mentor is required to be paired with at least one other mentor
            # split up multiple mentor names, strip leading / trailing white space, and put into an array
            self.mentorsRequired = [
                name.strip() for name in dataRow[position].split(multiItemDelimiter)
            ]
        position += 1

        # get comfort mentoring alone
        if dataRow[position] not in aloneComfortLevels:
            raise ValueError(
                "Got invalid value "
                + dataRow[position]
                + " for "
                + self.name
                + "'s team comfort mentoring alone in column "
                + str(position + 1)
            )
        self.comfortAlone = dataRow[position]
        position += 1

        # get transit type conveniences
        self.transitConveniences = []
        for transitType in range(numTypesTransit):
            if dataRow[position] not in transitConvenienceLevels:
                raise ValueError(
                    "Got invalid value "
                    + dataRow[position]
                    + " for "
                    + self.name
                    + "'s team transit convenience in column "
                    + str(position + 1)
                )
            self.transitConveniences.append(dataRow[position])
            position += 1

        # get confidence in skills
        self.skillsConfidence = []
        for skill in range(numSkills):
            if dataRow[position] not in skillConfidenceLevels:
                raise ValueError(
                    "Got invalid value "
                    + dataRow[position]
                    + " for "
                    + self.name
                    + "'s team skill confidence in column "
                    + str(position + 1)
                )
            self.skillsConfidence.append(dataRow[position])
            position += 1

    def isMatch(self, otherName):
        """
        Returns whether or not this mentor matches the input name
        Comparison ignores spaces and capitalization, but otherwise the names must match exactly
        """
        ownName = self.name.replace(" ", "").lower()
        otherName = otherName.replace(" ", "").lower()
        return ownName == otherName

    def mustPair(self, otherMentor):
        """
        Returns whether or otherMentor appears in this mentor's list of mentors they are required to be matched with
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
    for dataRow in mentorReader:
        mentors.append(
            Mentor(dataRow)
        )  # create a new mentor object based on each row of data
    return mentors
