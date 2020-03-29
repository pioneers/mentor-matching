"""
Constants for parsing team and mentors from CSV

This file is to later be broken down by constant usage
"""
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
# "1" is most uncomfortable mentoring alone
# "5" is very comfortable mentoring alone
comfortAloneLevels = ["1", "2", "3", "4", "5"]

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
