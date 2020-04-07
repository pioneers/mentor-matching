import io
from unittest.mock import MagicMock

import pytest

from mentor_matching.parameters import Parameters

yaml_text = """
minNumMentors: 1
maxNumMentors: 2
minMeetingTime: 60
totalMeetingTime: 90
teamOverlapValue: 10
mentorOverlapValue: 0
noOverlapCost: 10000
partialOverlapCost: 10000
teamTypeMatchValue: 500
teamRequestedValue: 900
teamRequiredValue: 200000
skillMatchValues:
  - - 0
    - 0
    - 0
    - 0
    - 0
  - - 0
    - 15
    - 25
    - 40
    - 50
  - - 0
    - 25
    - 50
    - 75
    - 100
  - - 0
    - 50
    - 100
    - 150
    - 200
  - - 0
    - 75
    - 150
    - 225
    - 300
comfortAloneCosts:
  - 1500
  - 1000
  - 500
  - 10
  - 1
required_mentor_teams:
  Scyther:
    - Metagross
  Nidoqueen:
    - Swampert
  Mew:
    - Cacturne
  Hitmonchan:
    - Metagross

required_mentor_mentors:
  Snorlax:
    - Exeggutor
  Seadra:
    - Lapras
  Primeape:
    - Starmie
  Lapras:
    - Seadra
  Dodrio:
    - Mew
"""

csv_text = """
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
required_mentor_mentors,bulbasaur,squirtle,charmander
required_mentor_teams,bulbasaur,chikorita,turtwig
"""


@pytest.fixture()
def csv_parameters():
    reader = io.StringIO(csv_text)
    return Parameters.from_csv(reader)


def test_from_yaml():
    reader = io.StringIO(yaml_text)
    parameters = Parameters.from_yaml(reader)
    assert 4 == len(parameters.required_mentor_teams)
    assert parameters.required_mentor_teams["Scyther"] == ["Metagross"]


def test_from_csv(csv_parameters):
    assert csv_parameters.minNumMentors == 1
    assert csv_parameters.required_mentor_mentors["bulbasaur"] == [
        "squirtle",
        "charmander",
    ]
    assert csv_parameters.required_mentor_teams["bulbasaur"] == ["chikorita", "turtwig"]


def test_required_mentor_team(csv_parameters):
    assert csv_parameters.required_mentor_team("bulbasaur", "chikorita")
    assert csv_parameters.required_mentor_team("bulbasaur", "turtwig")
    assert not csv_parameters.required_mentor_team("bulbasaur", "piplup")
    assert not csv_parameters.required_mentor_team("chikorita", "turtwig")


def test_required_mentor_mentor(csv_parameters):
    assert csv_parameters.required_mentor_mentor("bulbasaur", "squirtle")
    assert csv_parameters.required_mentor_mentor("bulbasaur", "charmander")
    assert csv_parameters.required_mentor_mentor("squirtle", "bulbasaur")
    assert not csv_parameters.required_mentor_mentor("squirtle", "charmander")
    assert not csv_parameters.required_mentor_mentor("bulbasaur", "aerodactyl")


def test_validate_names(csv_parameters):
    mentor_names = ["bulbasaur", "squirtle", "charmander", "caterpie", "weedle"]
    team_names = ["chikorita", "turtwig", "tropius"]

    def named_thing(name: str):
        m = MagicMock()
        m.name = name
        return m

    mentors = [named_thing(name) for name in mentor_names]
    teams = [named_thing(name) for name in team_names]

    # Normal case
    csv_parameters.validate_names(mentors, teams)

    # Illegal team
    csv_parameters.required_mentor_mentors["bulbasaur"].append("agumon")

    with pytest.raises(ValueError):
        csv_parameters.validate_names(mentors, teams)

    assert "agumon" == csv_parameters.required_mentor_mentors["bulbasaur"].pop()

    # Illegal mentor and team
    csv_parameters.required_mentor_mentors["katara"] = ["avatar"]

    with pytest.raises(ValueError):
        csv_parameters.validate_names(mentors, teams)
