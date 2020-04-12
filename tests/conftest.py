import pytest

from mentor_matching import csv_parsing


@pytest.fixture
def default_team_setup():
    return {
        "availability": [
            [True for _ in range(length)] for length in csv_parsing.slotsPerDay
        ],
        "team_types": [True, False, False, False],
        "transit_times": [5 for _ in range(csv_parsing.numTypesTransit)],
        "skill_requests": [
            csv_parsing.skillRequestLevels[0] for _ in range(csv_parsing.numSkills)
        ],
    }


@pytest.fixture
def default_parameters_setup():
    return {
        "minNumMentors": 0,
        "maxNumMentors": 1,
        "minMeetingTime": 0,
        "totalMeetingTime": 0,
        "teamOverlapValue": 0,
        "mentorOverlapValue": 0,
        "noOverlapCost": 0,
        "partialOverlapCost": 0,
        "teamTypeMatchValue": 0,
        "teamRequestedValue": 0,
        "skillMatchValues": [[0]],
        "comfortAloneCosts": list(range(5)),
        "required_mentor_groups": None,
        "required_team_assignments": None,
    }


@pytest.fixture
def default_mentor_setup():
    return {
        "availability": [
            [True for _ in range(length)] for length in csv_parsing.slotsPerDay
        ],
        "team_type_requests": [True, False, False, False],
        "teams_requested": [],
        "comfort_alone": csv_parsing.comfortAloneLevels[0],
        "transit_conveniences": [
            "Convenient" for _ in range(csv_parsing.numTypesTransit)
        ],
        "skills_confidence": ["Neutral" for _ in range(csv_parsing.numSkills)],
    }
