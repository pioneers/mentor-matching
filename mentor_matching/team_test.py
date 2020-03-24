import pytest

from mentor_matching.team import parse_availability


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
    assert expected == parse_availability(
        data, slots_per_day, available_mark, unavailable_mark,
    )
