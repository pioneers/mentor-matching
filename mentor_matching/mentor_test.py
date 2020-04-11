import csv
from typing import List
from unittest.mock import MagicMock

import pytest

from mentor_matching import csv_parsing
from mentor_matching.mentor import Mentor
from mentor_matching.mentor import validate_team_references


def test_from_string():
    raw_csv_line = [
        "Primeape,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,,,Starmie,1,Inconvenient,Convenient,Convenient,Not possible,Not possible,Somewhat,Very Confident"
    ]
    reader = csv.reader(raw_csv_line)
    processed_line = next(reader)
    mentor = Mentor.from_list(processed_line)

    assert mentor.name == "Primeape"
    assert mentor.teamTypeRequests == [1, 1, 0, 0]
    assert mentor.teamsRequested == []
    assert mentor.comfortAlone == csv_parsing.comfortAloneLevels[0]
    assert mentor.transitConveniences == [
        "Inconvenient",
        "Convenient",
        "Convenient",
        "Not possible",
        "Not possible",
    ]
    assert mentor.skillsConfidence == ["Somewhat", "Very Confident"]


@pytest.mark.parametrize(
    "requests,error_expected",
    [
        ([[], [], []], False),
        ([["misty"], [], ["brock"]], False),
        ([["oak"], [], ["dawn"]], True),
    ],
)
def test_validate_team_references(requests, error_expected):
    mentor_names = ["squirtle", "bulbasaur", "charmander"]
    team_names = ["ash", "misty", "brock"]

    def create_mentor(mentor_name: str, request: List[str]):
        m = MagicMock()
        m.name = mentor_name
        m.teamsRequested = request
        return m

    mentors = []
    for mentor_name, request in zip(mentor_names, requests):
        mentors.append(create_mentor(mentor_name, request))

    teams = [create_mentor(team_name, []) for team_name in team_names]

    try:
        validate_team_references(mentors, teams)
    except ValueError:
        assert error_expected is True
    else:
        assert error_expected is False
