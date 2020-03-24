"""
Spreadsheet formatting constants
"""
from typing import List

import pandas as pd

from mentor_matching.constants import minMeetingTime
from mentor_matching.constants import minutesPerSlot
from mentor_matching.constants import noOverlapCost
from mentor_matching.constants import numTeamTypes
from mentor_matching.constants import numTypesTransit
from mentor_matching.constants import partialOverlapCost
from mentor_matching.constants import slotsPerDay
from mentor_matching.constants import teamOverlapValue
from mentor_matching.constants import teamRequestedValue
from mentor_matching.constants import teamRequiredValue
from mentor_matching.constants import teamTypeMatchValue
from mentor_matching.constants import transitConvenienceLevels
from mentor_matching.constants import transitConvenienceWeights
from mentor_matching.mentor import Mentor
from mentor_matching.team import Team


"""
Functions for finding the value of a mentor-team pair, independent of any co-mentors
"""


def getTeamOverlapValue(mentor, team, transitType):
    """
    Measures how well the availability of a mentor's and team's availabilities overlap
    Assumes the mentor uses input transit type, which is an integer in range(numTransitTypes)
    Finds the total amount of overlap (minus travel time for the mentor), but an overlap must be for at least minMeetingTime to count
    Value is then total overlap time multiplied by teamOverlapValue and the transit convenience weight for that mentor and transit type
    If the transit type weight is zero for the mentor, returns -noOverlapCost
    If total overlap is zero, returns -noOverlapCost
    If total overlap is non-zero but less than totalMeetingTime, charges partialOverlapCost to the value (after weighting)

    Random note: there's an adversarial input to this where a small gap in the team's availability between two overlaps, combined
                    with a long travel time could cause the value to be overreported by giving a slot in the second overlap both
                    to that overlap and to travel time after the first overlap.  But I don't think this will actually come up
                    in practice, so I don't think it's worth futzing with the code to try to fix that.
    """
    totalOverlap = 0
    for day in range(7):
        # at the beginning of a day, reset all counters for contiguous blocks
        mentorAvailabilityBeforeOverlap = (
            0  # mentor may be able to travel before overlap happens
        )
        currOverlap = 0
        for slotNum in range(slotsPerDay[day]):
            if mentor.availability[day][slotNum] and team.availability[day][slotNum]:
                # this slot is part of an overlap, so start the overlap counter
                currOverlap += minutesPerSlot
            elif currOverlap > 0:
                # previously was in an overlap, but that just ended
                # need to figure out how much time the mentor is free after the overlap in case they can travel during that time
                mentorAvailabilityAfterOverlap = 0
                for afterSlot in range(slotNum, slotsPerDay[day]):
                    if mentor.availability[day][slotNum]:
                        mentorAvailabilityAfterOverlap += minutesPerSlot
                    else:
                        break  # found a gap in the mentor's availability, so stop counting
                if mentorAvailabilityBeforeOverlap < team.transitTimes[transitType]:
                    # mentor has to use up some of the overlap time to travel there
                    # else travel time before overlap doesn't interfere
                    currOverlap -= (
                        team.transitTimes[transitType] - mentorAvailabilityBeforeOverlap
                    )
                if mentorAvailabilityAfterOverlap < team.transitTimes[transitType]:
                    # mentor has to use up some of the overlap time to travel back
                    # else travel time after overlap doesn't interfere
                    currOverlap -= (
                        team.transitTimes[transitType] - mentorAvailabilityAfterOverlap
                    )
                if currOverlap >= minMeetingTime:
                    # enough of an overlap to count, so add it in
                    # else, just ignore this overlap
                    totalOverlap += currOverlap
                # overlap ended, so zero out all counters
                currOverlap = 0
                mentorAvailabilityBeforeOverlap = 0
            elif mentor.availability[day][slotNum]:
                # mentor has availability right now, but school doesn't
                # at best, this is time the mentor could use for travel before another overlap, so increment that counter
                mentorAvailabilityBeforeOverlap += minutesPerSlot
            else:
                # mentor has no availability and didn't just finish an overlap, so reset counters
                mentorAvailabilityBeforeOverlap = 0

        if currOverlap > 0:
            # means that the day ended with an overlap, so check to see if it is long enough (minus travel time)
            if mentorAvailabilityBeforeOverlap < team.transitTimes[transitType]:
                # need to charge for some amount of transit time before overlap
                currOverlap -= (
                    team.transitTimes[transitType] - mentorAvailabilityBeforeOverlap
                )
            # to be safe since we don't have data for later, I'll assume that the mentor has no availability afterwards
            # so we have to charge for the whole travel time at the end
            currOverlap -= team.transitTimes[transitType]
            if currOverlap >= minMeetingTime:
                totalOverlap += currOverlap

    # find the weight of this transit type for this mentor
    convenience = mentor.transitConveniences[transitType]
    weight = transitConvenienceWeights[
        transitConvenienceLevels.index(convenience)
    ]  # index between the weights and levels lists are the same
    value = totalOverlap * teamOverlapValue * weight

    if weight == 0:
        # this transit type is not good for this mentor, so treat it as if there were no overlap
        return -noOverlapCost
    if totalOverlap == 0:
        # no overlap found, so charge noOverlapCost
        return -noOverlapCost
    if totalOverlap < minMeetingTime:
        # have some overlap, but not as much as we'd want, so penalize the value somewhat
        value -= partialOverlapCost

    return value


def getTeamTypeValue(mentor: Mentor, team: Team):
    """
    Get the value for pairing a mentor with a team based on what type of team the mentor wants / what type the team is

    Random thought: as it is set up right now, it gives a flat value if there are any matches regardless of how many there are
                    based off our previous system, this makes sense since each team can only be one type
                    but in principle we could have multiple non-exclusive descriptors for a team, and give more value if there are more matches
    """
    for teamType in range(numTeamTypes):
        if mentor.teamTypeRequests[teamType] and team.teamTypes[teamType]:
            return teamTypeMatchValue
    return 0  # no matches :'(


def getTeamRequestedValue(mentor: Mentor, team: Team):
    """
    If the mentor must be matched with the team, returns teamRequiredValue
    If the mentor just requested the team, returns teamRequestedValue
    Else returns 0
    """
    for teamName in mentor.teamsRequired:
        if team.isMatch(teamName):
            return teamRequiredValue
    for teamName in mentor.teamsRequested:
        if team.isMatch(teamName):
            return teamRequestedValue
    return 0


def getTeamCompatibility(mentor: Mentor, team: Team) -> int:
    """
    Gets a "compatibility score" between a mentor and a team (used as the weight in the later optimization problem)
    Uses the functions defined above to compute different aspects of the score
    """
    score = 0

    # find value from overlapping availabilities
    # value may differ depending on transportation type used, so try them all
    bestOverlap = -noOverlapCost  # baseline to beat is no overlap at all
    for transitType in range(numTypesTransit):
        # check if this transit type is better than previous best and update if needed
        bestOverlap = max(bestOverlap, getTeamOverlapValue(mentor, team, transitType))
    score += bestOverlap

    # find value from team type matches
    score += getTeamTypeValue(mentor, team)

    # find value from team requests / requirements
    score += getTeamRequestedValue(mentor, team)

    return score


def create_team_compatability_data_frame(
    mentors: List[Mentor], teams: List[Team]
) -> pd.DataFrame:
    matrix: List[List[int]] = []
    for mentor in mentors:
        matrix.append([getTeamCompatibility(mentor, team) for team in teams])

    return pd.DataFrame(
        matrix,
        index=pd.Index([mentor.name for mentor in mentors], name="Name"),
        columns=[team.name for team in teams],
    )
