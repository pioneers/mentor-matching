"""
Constants for parsing team and mentors from CSV

Change this file to match the format of the mentor and team responses.
"""
from typing import Iterable
from typing import List

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


def parse_availability(
    data: List[str],
    slots_per_day: List[int],
    available_mark: str,
    unavailable_mark: str,
) -> List[List[bool]]:
    """
    Parse the availability given from a subsection of a CSV row.

    >>> parse_availability(
        ["1", "0", "0", "1"],
        [2, 2],
        "1",
        "0",
    )
    [[True, False], [False, True]]

    >>> parse_availability(
        ["present", "absent", "absent", "present"],
        [2, 1, 1],
        "present",
        "absent",
    )
    [[True, False], [False], [True]]
    """

    if len(data) != sum(slots_per_day):
        raise ValueError(
            f"Expected list of length {sum(slots_per_day)} but found list of length {len(data)}"
        )

    def parse_availability_mark(mark: str) -> bool:
        if mark == available_mark:
            return True
        elif mark == unavailable_mark:
            return False
        else:
            raise ValueError(f"Got invalid availability mark: {mark} in {data}")

    availability: List[List[bool]] = []

    position = 0
    for num_slots in slots_per_day:
        day_data = data[position : position + num_slots]
        day_availability = [parse_availability_mark(mark) for mark in day_data]
        availability.append(day_availability)
        position += num_slots

    return availability


def ensure_in_set(data: List[str], vocab: Iterable[str],) -> List[str]:
    """
    Ensure all elements of data are in vocab.

    vocab must support the in operator
    """

    def parse(mark: str) -> str:
        if mark not in vocab:
            raise ValueError(f"Got invalid mark {mark} in {data}")
        return mark

    return [parse(mark) for mark in data]


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


class Name(str):
    """
    Name defines how we want to compare names.

    Ignore case and surrounding white space.
    """

    def __eq__(self, other):
        return self.strip().lower() == other.strip().lower()

    __hash__ = str.__hash__
