import logging
from unittest.mock import MagicMock

import pytest

from mentor_matching.cli import DEFAULT_PARAMETERS_LOCATION
from mentor_matching.parameters import Parameters

logger = logging.getLogger(__name__)


def test_from_yaml():
    with open("data/parameters.yaml") as parameters_file:
        parameters = Parameters.from_yaml(parameters_file)
    assert parameters.minNumMentors == 1
    assert parameters.maxNumMentors == 2

    assert parameters.must_pair(entity("Snorlax"), entity("Exeggutor"))
    assert parameters.must_pair(entity("Seadra"), entity("Lapras"))
    assert not parameters.must_pair(entity("Seadra"), entity("Bulbasaur"))


def test_from_csv():
    with open("data/parameters.csv") as parameters_file:
        parameters = Parameters.from_csv(parameters_file)
    assert parameters.minNumMentors == 1


def test_from_default():
    with open(DEFAULT_PARAMETERS_LOCATION) as parameters_file:
        parameters = Parameters.from_csv(parameters_file)
    assert parameters.minNumMentors == 1


def entity(name: str):
    m = MagicMock()
    m.name = name
    return m


def test_must_pair(default_parameters_setup):
    mentor_groups = [
        ["bulbasaur", "charmander", "squirtle"],
        ["torchic", "mudkip"],
    ]
    default_parameters_setup["required_mentor_groups"] = mentor_groups
    parameters = Parameters(**default_parameters_setup)
    assert parameters.must_pair(entity("bulbasaur"), entity("charmander"))
    assert parameters.must_pair(entity("bulbasaur"), entity("squirtle"))
    assert parameters.must_pair(entity("charmander"), entity("squirtle"))
    assert parameters.must_pair(entity("torchic"), entity("mudkip"))
    assert not parameters.must_pair(entity("torchic"), entity("agumon"))
    assert not parameters.must_pair(entity("torchic"), entity("bulbasaur"))


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


def test_must_assign(default_parameters_setup):
    assignments = {
        "bulbasaur": "ash",
        "squirtle": "ash",
        "starmie": "misty",
    }
    default_parameters_setup["required_team_assignments"] = assignments
    parameters = Parameters(**default_parameters_setup)
    assert parameters.must_assign("bulbasaur", "ash")
    assert parameters.must_assign("squirtle", "ash")
    assert not parameters.must_assign("starmie", "ash")
    assert parameters.must_assign("starmie", "misty")
    assert not parameters.must_assign("squirtle", "misty")
    assert not parameters.must_assign("bulbasaur", "satoshi")
    assert not parameters.must_assign("agumon", "satoshi")
