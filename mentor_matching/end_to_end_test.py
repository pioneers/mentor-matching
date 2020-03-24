from mentor_matching.match import match
from mentor_matching.mentor import mentors_from_file
from mentor_matching.team import teams_from_file


def test_end_to_end():
    with open("data/mentors-example.csv") as mentorFile:
        mentors = mentors_from_file(mentorFile)

    with open("data/teams-example.csv") as team_file:
        teams = teams_from_file(team_file)

    var_set = match(mentors, teams)
    matching = var_set.team_by_mentor()
    assert matching is not None

    expected_matching = {
        "Mavericl": "Skyline HS",
        "Stephen": "Oakland School for the Arts",
        "Starr": "Pinole Valley High",
        "Yuqing Xu": "Hercules",
        "Sophia X": "Making Waves Academy",
        "Justin T": "John Henry Highschool",
        "Aidan": "Berkeley Technology Academy",
        "Kevin": "Saint Mary's College High School",
        "Juan": "Making Waves Academy",
        "Joel": "John Henry Highschool",
        "Xochitl": "El Cerrito High school",
        "Pragyan": "Salesian High School",
        "Anvita": "Bishop O'Dowd",
        "Iram": "Arroyo",
        "Mohamed": "El Cerrito High school",
        "Xiaojing (Ivy)": "Arroyo",
        "Lana": "Berkeley Technology Academy",
        "Jing": "Albany High School",
        "Jessica": "Skyline HS",
        "Benjamin": "Bishop O'Dowd",
        "Monet": "Saint Mary's College High School",
        "Melany": "ACLC, Alameda Community Learning Center",
        "Andrew": "ACLC, Alameda Community Learning Center",
        "Janek": "Hercules",
        "Michelle": "Pinole Valley High",
        "America": "LPS Richmond",
        "Hisham": "Albany High School",
        "Justin S": "Oakland School for the Arts",
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
        print(err)
    assert len(errors) == 0
