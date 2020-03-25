import csv

from mentor_matching.constants import AloneComfortLevel
from mentor_matching.mentor import Mentor


def test_from_string():
    raw_csv_line = [
        "Mavericl,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,,,Jessica,1,Inconvenient,Convenient,Convenient,Not possible,Not possible,Somewhat,Very Confident"
    ]
    reader = csv.reader(raw_csv_line)
    processed_line = next(reader)
    mentor = Mentor.from_list(processed_line)

    assert mentor.name == "Mavericl"
    assert mentor.teamTypeRequests == [1, 1, 0, 0]
    assert mentor.teamsRequested == []
    assert mentor.teamsRequired == []
    assert mentor.mentorsRequired == ["Jessica"]
    assert mentor.comfortAlone == AloneComfortLevel.LEAST
    assert mentor.transitConveniences == [
        "Inconvenient",
        "Convenient",
        "Convenient",
        "Not possible",
        "Not possible",
    ]
    assert mentor.skillsConfidence == ["Somewhat", "Very Confident"]
