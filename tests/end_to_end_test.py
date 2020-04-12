import logging

from mentor_matching.match import match
from mentor_matching.mentor import Mentor
from mentor_matching.mentor import mentors_from_file
from mentor_matching.parameters import Parameters
from mentor_matching.team import Team
from mentor_matching.team import teams_from_file


logger = logging.getLogger(__name__)


def test_no_solution(
    default_mentor_setup, default_team_setup, default_parameters_setup
):
    """Try creating constraints such that there is no valid solution."""
    default_mentor_setup["name"] = "charmander"
    charmander = Mentor(**default_mentor_setup)

    default_mentor_setup["name"] = "squirtle"
    squirtle = Mentor(**default_mentor_setup)

    mentors = [charmander, squirtle]

    default_team_setup["name"] = "ash"
    ash = Team(**default_team_setup)
    default_team_setup["name"] = "misty"
    misty = Team(**default_team_setup)
    teams = [ash, misty]

    # Require both mentors go to one team, even though we require all teams to
    # have at least one mentor
    default_parameters_setup["required_team_assignments"] = {
        "charmander": "ash",
        "squirtle": "ash",
    }
    parameters = Parameters(**default_parameters_setup)

    assignment_set = match(mentors, teams, parameters)
    assert assignment_set is None


def test_end_to_end():
    """
    Ensure mentor_matching continues to produce the same matching, given
    the same inputs.
    """

    with open("data/mentors-example.csv") as mentorFile:
        mentors = mentors_from_file(mentorFile)

    with open("data/teams-example.csv") as team_file:
        teams = teams_from_file(team_file)

    parameters = Parameters.from_file("data/parameters.yaml")

    assignment_set = match(mentors, teams, parameters)
    matching = assignment_set.team_by_mentor()
    assert matching is not None

    expected_matching = {
        "Lapras": "Spinda",
        "Parasect": "Walrein",
        "Lickitung": "Walrein",
        "Scyther": "Metagross",
        "Electrode": "Chimecho",
        "Sandslash": "Salamence",
        "Exeggutor": "Shiftry",
        "Seadra": "Spinda",
        "Nidoqueen": "Armaldo",
        "Primeape": "Dusclops",
        "Mew": "Swalot",
        "Aerodactyl": "Hariyama",
        "Hitmonchan": "Metagross",
        "Seaking": "Armaldo",
        "Porygon": "Dustox",
        "Dodrio": "Swalot",
        "Wigglytuff": "Swampert",
        "Venusaur": "Chimecho",
        "Snorlax": "Shiftry",
        "Slowbro": "Cacturne",
        "Starmie": "Dusclops",
        "Kangaskhan": "Swampert",
        "Kabutops": "Cacturne",
        "Tangela": "Relicanth",
        "Gyarados": "Sableye",
        "Ditto": "Hariyama",
        "Weezing": "Relicanth",
        "Vileplume": "Sableye",
    }
    assert len(matching) == len(expected_matching)

    errors = []
    for mentor in matching:
        actual_team_name = matching[mentor].name
        expected_team_name = expected_matching[mentor.name]
        if expected_team_name != actual_team_name:
            errors.append(
                f"expected {mentor.name} to match with {expected_team_name} but got {actual_team_name}"
            )

    for err in errors:
        logger.error(err)
    assert len(errors) == 0
