import csv

from mentor_matching import constants
from mentor_matching.mentor import Mentor


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
    assert mentor.teamsRequired == []
    assert mentor.mentorsRequired == ["Starmie"]
    assert mentor.comfortAlone == constants.comfortAloneLevels[0]
    assert mentor.transitConveniences == [
        "Inconvenient",
        "Convenient",
        "Convenient",
        "Not possible",
        "Not possible",
    ]
    assert mentor.skillsConfidence == ["Somewhat", "Very Confident"]
