import io

from mentor_matching.objective_set import Parameters


def test_from_csv():
    raw_text = """
# Number of mentors per team,,,,,,,,,,,,,,,,,,,,,,,,,
# minimum number of mentors that can be assigned to a team,,,,,,,,,,,,,,,,,,,,,,,,,
minNumMentors,1,,,,,,,,,,,,,,,,,,,,,,,,
# maximum number of mentors that can be assigned to a team,,,,,,,,,,,,,,,,,,,,,,,,,
maxNumMentors,2,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
# Availability overlap,,,,,,,,,,,,,,,,,,,,,,,,,
# minimum number of minutes a mentor's / team's availabilities need to overlap in order to count,,,,,,,,,,,,,,,,,,,,,,,,,
minMeetingTime,60,,,,,,,,,,,,,,,,,,,,,,,,
# how many minutes per week we want mentors to be with their teams,,,,,,,,,,,,,,,,,,,,,,,,,
totalMeetingTime,90,,,,,,,,,,,,,,,,,,,,,,,,
# how much each minute of availability overlap between a team and mentor is valued,,,,,,,,,,,,,,,,,,,,,,,,,
teamOverlapValue,10,,,,,,,,,,,,,,,,,,,,,,,,
# how much each minute of availability overlap between two mentors is valued,,,,,,,,,,,,,,,,,,,,,,,,,
mentorOverlapValue,0,,,,,,,,,,,,,,,,,,,,,,,,
# how much cost to incur if a mentor and team don't have any availabilities at the same times (should be very large),,,,,,,,,,,,,,,,,,,,,,,,,
noOverlapCost,10000,,,,,,,,,,,,,,,,,,,,,,,,
"# how much cost to incur if there is some overlap, but less than totalMeetingTime",,,,,,,,,,,,,,,,,,,,,,,,,
partialOverlapCost,10000,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
# Team types,,,,,,,,,,,,,,,,,,,,,,,,,
# how much value to give if a team is of a type the mentor wants,,,,,,,,,,,,,,,,,,,,,,,,,
teamTypeMatchValue,500,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
# Team requests,,,,,,,,,,,,,,,,,,,,,,,,,
# how much value to give if a mentor requested to work with a team,,,,,,,,,,,,,,,,,,,,,,,,,
teamRequestedValue,900,,,,,,,,,,,,,,,,,,,,,,,,
# how much value to give if a mentor *must* be matched with this team,,,,,,,,,,,,,,,,,,,,,,,,,
teamRequiredValue,200000,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,
# Skills,,,,,,,,,,,,,,,,,,,,,,,,,
# how much value to give depending on how confident a mentor is in a skill and how much a team wants it,,,,,,,,,,,,,,,,,,,,,,,,,
"# each subarray corresponds to a team request level, from least important to most",,,,,,,,,,,,,,,,,,,,,,,,,
"# each entry in a subarray corresponds to a mentor confidence level, from least to most",,,,,,,,,,,,,,,,,,,,,,,,,
skillMatchValues,0,0,0,0,0,0,15,25,40,50,0,25,50,75,100,0,50,100,150,200,0,75,150,225,300
,,,,,,,,,,,,,,,,,,,,,,,,,
# Comfort Cost,,,,,,,,,,,,,,,,,,,,,,,,,
# The first element is the cost when the mentor is the least comfortable,,,,,,,,,,,,,,,,,,,,,,,,,
# mentoring alone,,,,,,,,,,,,,,,,,,,,,,,,,
# The last element is the cost when the mentor is the most comfortable,,,,,,,,,,,,,,,,,,,,,,,,,
# mentoring alone.,,,,,,,,,,,,,,,,,,,,,,,,,
# Typically this list would be in decreasing order.,,,,,,,,,,,,,,,,,,,,,,,,,
comfortAloneCosts,1500,1000,500,10,1,,,,,,,,,,,,,,,,,,,,
    """
    reader = io.StringIO(raw_text)
    parameters = Parameters.from_csv(reader)
    assert parameters.minNumMentors == 1