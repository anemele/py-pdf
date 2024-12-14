import pytest

from .booklet import resort_from_booklet, resort_to_booklet


def test_resort_from_booklet():
    assert resort_from_booklet([8, 1, 2, 7, 6, 3, 4, 5]) == [1, 2, 3, 4, 5, 6, 7, 8]  # type: ignore
    assert resort_from_booklet([4, 1, 2, 3]) == [1, 2, 3, 4]  # type: ignore

    with pytest.raises(ValueError):
        resort_from_booklet([1, 2, 3])  # type: ignore


def test_resort_to_booklet():
    # type: ignore
    assert resort_to_booklet([1, 2, 3, 4, 5, 6, 7, 8], 0) == [8, 1, 2, 7, 6, 3, 4, 5]  # type: ignore
    assert resort_to_booklet([1, 2, 3, 4, 5, 6, 7], 0) == [0, 1, 2, 7, 6, 3, 4, 5]  # type: ignore
    assert resort_to_booklet([1, 2, 3, 4, 5, 6], 0) == [0, 1, 2, 0, 6, 3, 4, 5]  # type: ignore
    assert resort_to_booklet([1, 2, 3, 4, 5], 0) == [0, 1, 2, 0, 0, 3, 4, 5]  # type: ignore
    assert resort_to_booklet([1, 2, 3, 4], 0) == [4, 1, 2, 3]  # type: ignore
