import csv

import pytest

from mentor_matching import csv_parsing
from mentor_matching.team import Team


@pytest.mark.parametrize(
    "data,slots_per_day,available_mark,unavailable_mark,expected",
    [
        (["1", "0", "0", "1"], [2, 2], "1", "0", [[True, False], [False, True]],),
        (["1", "0", "0", "1"], [2, 1, 1], "1", "0", [[True, False], [False], [True]],),
        (["Sure", "Nah"], [1, 1], "Sure", "Nah", [[True], [False]],),
    ],
)
def test_parse_availability(
    data, slots_per_day, available_mark, unavailable_mark, expected,
):
    assert expected == csv_parsing.parse_availability(
        data, slots_per_day, available_mark, unavailable_mark,
    )


def test_from_string():
    raw_csv_line = [
        "Dustox,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,76,76,36,36,36,4,4",
    ]
    reader = csv.reader(raw_csv_line)
    processed_line = next(reader)
    team = Team.from_list(processed_line)

    assert team.name == "Dustox"
    assert team.teamTypes == [False, False, False, True]
    assert team.transitTimes == [76, 76, 36, 36, 36]
    assert team.skillRequests == ["4", "4"]
