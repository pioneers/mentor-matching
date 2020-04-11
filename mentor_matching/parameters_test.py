from unittest.mock import MagicMock

from mentor_matching.cli import DEFAULT_PARAMETERS_LOCATION
from mentor_matching.parameters import Parameters


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


def test_must_pair():
    mentor_groups = [
        ["bulbasaur", "charmander", "squirtle"],
        ["torchic", "mudkip"],
    ]
    parameters = Parameters(
        0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, [[0]], list(range(5)), mentor_groups
    )
    assert parameters.must_pair(entity("bulbasaur"), entity("charmander"))
    assert parameters.must_pair(entity("bulbasaur"), entity("squirtle"))
    assert parameters.must_pair(entity("charmander"), entity("squirtle"))
    assert parameters.must_pair(entity("torchic"), entity("mudkip"))
    assert not parameters.must_pair(entity("torchic"), entity("agumon"))
    assert not parameters.must_pair(entity("torchic"), entity("bulbasaur"))


def test_must_assign():
    assignments = {
        "bulbasaur": "ash",
        "squirtle": "ash",
        "starmie": "misty",
    }
    parameters = Parameters(
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        [[0]],
        list(range(5)),
        required_team_assignments=assignments,
    )
    assert parameters.must_assign("bulbasaur", "ash")
    assert parameters.must_assign("squirtle", "ash")
    assert not parameters.must_assign("starmie", "ash")
    assert parameters.must_assign("starmie", "misty")
    assert not parameters.must_assign("squirtle", "misty")
    assert not parameters.must_assign("bulbasaur", "satoshi")
    assert not parameters.must_assign("agumon", "satoshi")
