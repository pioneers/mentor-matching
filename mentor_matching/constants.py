"""
Holds constants.

This file is to later be broken down by constant usage
"""
# Basic formatting
mentorHeaderRows = (
    1  # how many of the rows in the mentor sheet are headers and so should be ignored
)
teamHeaderRows = (
    1  # how many of the rows in the team sheet are headers and so should be ignored
)
multiItemDelimiter = ";"  # what character is used to separate entries in cells that may have multiple values
# CANNOT be a comma, since that will create problems with the csv formatting

# Availability information
minutesPerSlot = 30  # number of minutes each slot accounts for
slotsPerDay = [
    24,
    24,
    24,
    24,
    24,
    24,
    24,
]  # how many slots occur on each day--list in order they appear on the spreadsheet
availableMark = (
    "1"  # what will appear in a slot if a mentor / team is available at that time
)
unavailableMark = (
    "0"  # what will appear in a slot if a mentor / team is *not* available at that time
)

# Team types
numTeamTypes = 4  # how many team types we've defined / let mentors choose from
teamTypeYesMark = (
    "1"  # what will appear if a mentor wants a team type / a team is that type
)
teamTypeNoMark = "0"  # what will appear if a mentor doesn't want a team type / the team isn't that type

# Mentoring alone
aloneComfortLevels = [
    "1",
    "2",
    "3",
    "4",
    "5",
]  # comfort levels mentors can put down for mentoring alone

# Transit
numTypesTransit = 5  # number of different types of transit we ask mentors / teams about
transitConvenienceLevels = [
    "Not possible",
    "Inconvenient",
    "Convenient",
]  # convenience levels mentors can put down for transit types

# Skills
numSkills = (
    2  # how many skills we ask mentors for confidence in / teams for how much they want
)
skillConfidenceLevels = [
    "Not Confident",
    "Somewhat",
    "Neutral",
    "Confident",
    "Very Confident",
]  # confidence levels mentors can put down for skills
# should be arranged from least to most confident
skillRequestLevels = [
    "5",
    "4",
    "3",
    "2",
    "1",
]  # levels that teams can say they want mentors with a given school, from least to most


"""
Weights and other matching-related constants
"""

# Number of mentors per team
minNumMentors = 1  # minimum number of mentors that can be assigned to a team
maxNumMentors = 2  # maximum number of mentors that can be assigned to a team

# Availability overlap
minMeetingTime = 60  # minimum number of minutes a mentor's / team's availabilities need to overlap in order to count
totalMeetingTime = (
    90  # how many minutes per week we want mentors to be with their teams
)
teamOverlapValue = 10  # how much each minute of availability overlap between a team and mentor is valued
mentorOverlapValue = (
    0  # how much each minute of availability overlap between two mentors is valued
)
noOverlapCost = 10000  # how much cost to incur if a mentor and team don't have any availabilities at the same times (should be very large)
partialOverlapCost = 10000  # how much cost to incur if there is some overlap, but less than totalMeetingTime

# Team types
teamTypeMatchValue = (
    500  # how much value to give if a team is of a type the mentor wants
)

# Team requests
teamRequestedValue = (
    900  # how much value to give if a mentor requested to work with a team
)
teamRequiredValue = (
    200000  # how much value to give if a mentor *must* be matched with this team
)

# Mentoring alone
aloneComfortCosts = [
    1500,
    1000,
    500,
    10,
    1,
]  # how much cost to incur for mentoring alone based on comfort level
# note that the order of this must match that of aloneComfortLevels (from above)

# Transit
transitConvenienceWeights = [
    0,
    0.6,
    1,
]  # how much the value of an overlap should be weighted based on convenience of transit required
# setting a weight to 0 will mean that we don't consider travel types of that convenience

# Skills
skillMatchValues = [
    [
        0,
        0,
        0,
        0,
        0,
    ],  # how much value to give depending on how confident a mentor is in a skill and how much a team wants it
    [
        0,
        15,
        25,
        40,
        50,
    ],  # each subarray corresponds to a team request level, from least important to most
    [
        0,
        25,
        50,
        75,
        100,
    ],  # each entry in a subarray corresponds to a mentor confidence level, from least to most
    [0, 50, 100, 150, 200],
    [0, 75, 150, 225, 300],
]
