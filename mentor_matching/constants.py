"""
Holds constants.

This file is to later be broken down by constant usage
"""
from enum import Enum

# Basic formatting
# how many of the rows in the mentor sheet are headers and so should be ignored
mentorHeaderRows = 1
# how many of the rows in the team sheet are headers and so should be ignored
teamHeaderRows = 1
# what character is used to separate entries in cells that may have multiple values
# CANNOT be a comma, since that will create problems with the csv formatting
multiItemDelimiter = ";"

# Availability information

# number of minutes each slot accounts for
minutesPerSlot = 30
# how many slots occur on each day--list in order they appear on the spreadsheet
slotsPerDay = [
    24,
    24,
    24,
    24,
    24,
    24,
    24,
]

# what will appear in a slot if a mentor / team is available at that time
availableMark = "1"

# what will appear in a slot if a mentor / team is *not* available at that time
unavailableMark = "0"

# Team types
# how many team types we've defined / let mentors choose from
numTeamTypes = 4
# what will appear if a mentor wants a team type / a team is that type
teamTypeYesMark = "1"
# what will appear if a mentor doesn't want a team type / the team isn't that type
teamTypeNoMark = "0"


# Mentoring alone
# comfort levels mentors can put down for mentoring alone
class AloneComfortLevel(Enum):
    LEAST = "1"
    LESS = "2"
    MEDIUM = "3"
    MORE = "4"
    MOST = "5"

    def cost(self):
        alone_comfort_costs = {
            AloneComfortLevel.LEAST: 1500,
            AloneComfortLevel.LESS: 1000,
            AloneComfortLevel.MEDIUM: 500,
            AloneComfortLevel.MORE: 10,
            AloneComfortLevel.MOST: 1,
        }
        return alone_comfort_costs[self]


# Transit
# number of different types of transit we ask mentors / teams about
numTypesTransit = 5

# Maps convenience levels mentors can put down for transit types
# to how much the value of an overlap should be weighted based on
# convenience of transit required.
#
# Setting a weight to 0 will mean that we don't consider travel types of
# that convenience.
transit_convenience = {
    "Not possible": 0,
    "Inconvenient": 0.6,
    "Convenient": 1,
}

# Skills
# how many skills we ask mentors for confidence in / teams for how much they want
numSkills = 2

# confidence levels mentors can put down for skills
# should be arranged from least to most confident
skillConfidenceLevels = [
    "Not Confident",
    "Somewhat",
    "Neutral",
    "Confident",
    "Very Confident",
]


# levels that teams can say they want mentors with a given school, from least to most
skillRequestLevels = [
    "5",
    "4",
    "3",
    "2",
    "1",
]


"""
Weights and other matching-related constants
"""

# Number of mentors per team
minNumMentors = 1  # minimum number of mentors that can be assigned to a team
maxNumMentors = 2  # maximum number of mentors that can be assigned to a team

# Availability overlap
# minimum number of minutes a mentor's / team's availabilities need to overlap in order to count
minMeetingTime = 60
# how many minutes per week we want mentors to be with their teams
totalMeetingTime = 90
# how much each minute of availability overlap between a team and mentor is valued
teamOverlapValue = 10
# how much each minute of availability overlap between two mentors is valued
mentorOverlapValue = 0
# how much cost to incur if a mentor and team don't have any availabilities at the same times (should be very large)
noOverlapCost = 10000
# how much cost to incur if there is some overlap, but less than totalMeetingTime
partialOverlapCost = 10000

# Team types
# how much value to give if a team is of a type the mentor wants
teamTypeMatchValue = 500

# Team requests
# how much value to give if a mentor requested to work with a team
teamRequestedValue = 900
# how much value to give if a mentor *must* be matched with this team
teamRequiredValue = 200000

# Skills
skillMatchValues = [
    # how much value to give depending on how confident a mentor is in a skill and how much a team wants it
    [0, 0, 0, 0, 0],
    # each subarray corresponds to a team request level, from least important to most
    [0, 15, 25, 40, 50],
    # each entry in a subarray corresponds to a mentor confidence level, from least to most
    [0, 25, 50, 75, 100],
    [0, 50, 100, 150, 200],
    [0, 75, 150, 225, 300],
]
