import pytest

from py_pdf.utils import sort_from_booklet, sort_to_booklet


def test_sort_from_booklet():
    assert sort_from_booklet([8, 1, 2, 7, 6, 3, 4, 5]) == [1, 2, 3, 4, 5, 6, 7, 8]
    assert sort_from_booklet([4, 1, 2, 3]) == [1, 2, 3, 4]

    with pytest.raises(ValueError):
        sort_from_booklet([1, 2, 3])


def test_sort_to_booklet():
    assert sort_to_booklet([1, 2, 3, 4, 5, 6, 7, 8]) == [8, 1, 2, 7, 6, 3, 4, 5]
    assert sort_to_booklet([1, 2, 3, 4]) == [4, 1, 2, 3]

    with pytest.raises(ValueError):
        sort_to_booklet([1, 2, 3])
