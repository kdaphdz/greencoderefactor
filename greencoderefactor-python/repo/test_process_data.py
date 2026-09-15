import pytest
from process_data import process_data
from operations import operate

@pytest.mark.parametrize(
    "x, data, expected",
        [
        (1, [1, 2, 3], [2, 4, 6]),
        (0, [1, 2, 3], [3, 6, 9]),
        (2, [4, 5], [12, 15]),
        (5, [], []),
        ],
    )

def test_process_data(x, data, expected):
    assert process_data(x, data) == expected

def test_operate():
    assert operate() == 50
