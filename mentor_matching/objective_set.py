from typing import List

import cvxpy as cv
import pandas as pd

from mentor_matching import csv_parsing
from mentor_matching.assignment_set import AssignmentSet
from mentor_matching.assignment_set import AssignmentType
from mentor_matching.mentor import Mentor
from mentor_matching.parameters import Parameters
from mentor_matching.team import Team


def comfort_alone_level_to_cost(
    parameters: Parameters, comfort_alone_level: str
) -> int:
    """
    Translate a comfort_alone_cost_level to its cost

    Creates a dict that maps levels to costs, then uses that dict
    """
    level_to_cost = dict(
        zip(csv_parsing.comfortAloneLevels, parameters.comfortAloneCosts)
    )
    return level_to_cost[comfort_alone_level]


class ObjectiveSet(object):
    def __init__(self, assignment_set: AssignmentSet, parameters: Parameters):
        self._assignment_set = assignment_set
        self.parameters = parameters
        # list of terms that will be added together to make the objective function
        self._objective_terms: List[cv.expressions.expression.Expression] = []
        self._create_solo_mentor_terms()
        self._create_group_mentor_terms()

    def _create_solo_mentor_terms(self) -> None:
        for var in self._assignment_set.by_type[AssignmentType.SoloMentor]:
            _, mentor, team = self._assignment_set.assignment_group[var]
            value = self.get_team_compatability(
                mentor, team
            ) - comfort_alone_level_to_cost(self.parameters, mentor.comfortAlone)
            self._objective_terms.append(value * var)

    def _create_group_mentor_terms(self) -> None:
        for var in self._assignment_set.by_type[AssignmentType.GroupMentor]:
            # figure out which mentor and team this variable is for
            _, mentor, team = self._assignment_set.assignment_group[var]
            value = self.get_team_compatability(mentor, team)
            self._objective_terms.append(value * var)

    def objective(self):
        return sum(self._objective_terms)

    def get_team_overlap_value(self, mentor, team, transit_type):
        """
        Measures how well the availability of a mentor's and team's availabilities overlap
        Assumes the mentor uses input transit type, which is an integer in range(numTransitTypes)
        Finds the total amount of overlap (minus travel time for the mentor), but an overlap must be for at least self.parameters.minMeetingTime to count
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
        for day, slots_in_day in enumerate(csv_parsing.slotsPerDay):
            # at the beginning of a day, reset all counters for contiguous blocks
            # mentor may be able to travel before overlap happens
            mentorAvailabilityBeforeOverlap = 0
            currOverlap = 0
            for slotNum in range(slots_in_day):
                if (
                    mentor.availability[day][slotNum]
                    and team.availability[day][slotNum]
                ):
                    # this slot is part of an overlap, so start the overlap counter
                    currOverlap += csv_parsing.minutesPerSlot
                elif currOverlap > 0:
                    # previously was in an overlap, but that just ended
                    # need to figure out how much time the mentor is free after the overlap in case they can travel during that time
                    mentorAvailabilityAfterOverlap = 0
                    for afterSlot in range(slotNum, slots_in_day):
                        if mentor.availability[day][slotNum]:
                            mentorAvailabilityAfterOverlap += csv_parsing.minutesPerSlot
                        else:
                            break  # found a gap in the mentor's availability, so stop counting
                    if (
                        mentorAvailabilityBeforeOverlap
                        < team.transitTimes[transit_type]
                    ):
                        # mentor has to use up some of the overlap time to travel there
                        # else travel time before overlap doesn't interfere
                        currOverlap -= (
                            team.transitTimes[transit_type]
                            - mentorAvailabilityBeforeOverlap
                        )
                    if mentorAvailabilityAfterOverlap < team.transitTimes[transit_type]:
                        # mentor has to use up some of the overlap time to travel back
                        # else travel time after overlap doesn't interfere
                        currOverlap -= (
                            team.transitTimes[transit_type]
                            - mentorAvailabilityAfterOverlap
                        )
                    if currOverlap >= self.parameters.minMeetingTime:
                        # enough of an overlap to count, so add it in
                        # else, just ignore this overlap
                        totalOverlap += currOverlap
                    # overlap ended, so zero out all counters
                    currOverlap = 0
                    mentorAvailabilityBeforeOverlap = 0
                elif mentor.availability[day][slotNum]:
                    # mentor has availability right now, but school doesn't
                    # at best, this is time the mentor could use for travel before another overlap, so increment that counter
                    mentorAvailabilityBeforeOverlap += csv_parsing.minutesPerSlot
                else:
                    # mentor has no availability and didn't just finish an overlap, so reset counters
                    mentorAvailabilityBeforeOverlap = 0

            if currOverlap > 0:
                # means that the day ended with an overlap, so check to see if it is long enough (minus travel time)
                if mentorAvailabilityBeforeOverlap < team.transitTimes[transit_type]:
                    # need to charge for some amount of transit time before overlap
                    currOverlap -= (
                        team.transitTimes[transit_type]
                        - mentorAvailabilityBeforeOverlap
                    )
                # to be safe since we don't have data for later, I'll assume that the mentor has no availability afterwards
                # so we have to charge for the whole travel time at the end
                currOverlap -= team.transitTimes[transit_type]
                if currOverlap >= self.parameters.minMeetingTime:
                    totalOverlap += currOverlap

        # find the weight of this transit type for this mentor
        convenience = mentor.transitConveniences[transit_type]
        weight = csv_parsing.transit_convenience[convenience]

        value = totalOverlap * self.parameters.teamOverlapValue * weight

        if weight == 0:
            # this transit type is not good for this mentor, so treat it as if there were no overlap
            return -self.parameters.noOverlapCost
        if totalOverlap == 0:
            # no overlap found, so charge noOverlapCost
            return -self.parameters.noOverlapCost
        if totalOverlap < self.parameters.minMeetingTime:
            # have some overlap, but not as much as we'd want, so penalize the value somewhat
            value -= self.parametesr["partialOverlapCost"]

        return value

    def get_team_type_value(self, mentor: Mentor, team: Team):
        """
        Get the value for pairing a mentor with a team based on what type of team the mentor wants / what type the team is

        Random thought: as it is set up right now, it gives a flat value if there are any matches regardless of how many there are
                        based off our previous system, this makes sense since each team can only be one type
                        but in principle we could have multiple non-exclusive descriptors for a team, and give more value if there are more matches
        """
        for teamType in range(csv_parsing.numTeamTypes):
            if mentor.teamTypeRequests[teamType] and team.teamTypes[teamType]:
                return self.parameters.teamTypeMatchValue
        return 0  # no matches :'(

    def get_team_requested_value(self, mentor: Mentor, team: Team):
        """
        If the mentor must be matched with the team, returns teamRequiredValue
        If the mentor just requested the team, returns teamRequestedValue
        Else returns 0
        """
        if self.parameters.must_assign(mentor.name, team.name):
            return self.parameters.teamRequiredValue
        if team.name in mentor.teamsRequested:
            return self.parameters.teamRequestedValue
        return 0

    def get_team_compatability(self, mentor: Mentor, team: Team) -> int:
        """
        Gets a "compatibility score" between a mentor and a team (used as the weight in the later optimization problem)
        Uses the functions defined above to compute different aspects of the score
        """
        score = 0

        # find value from overlapping availabilities
        # value may differ depending on transportation type used, so try them all
        # baseline to beat is no overlap at all
        bestOverlap = -self.parameters.noOverlapCost
        for transit_type in range(csv_parsing.numTypesTransit):
            # check if this transit type is better than previous best and update if needed
            bestOverlap = max(
                bestOverlap, self.get_team_overlap_value(mentor, team, transit_type)
            )
        score += bestOverlap

        # find value from team type matches
        score += self.get_team_type_value(mentor, team)

        # find value from team requests / requirements
        score += self.get_team_requested_value(mentor, team)

        return score

    def create_team_compatability_data_frame(
        self, mentors: List[Mentor], teams: List[Team]
    ) -> pd.DataFrame:
        matrix: List[List[int]] = []
        for mentor in mentors:
            matrix.append([self.get_team_compatability(mentor, team) for team in teams])

        return pd.DataFrame(
            matrix,
            index=pd.Index([mentor.name for mentor in mentors], name="Name"),
            columns=[team.name for team in teams],
        )
