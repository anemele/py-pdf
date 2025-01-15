from pathlib import Path

from py_pdf.statpage import PathAndCount, stat_pdf

A4 = Path("tests/sample/A4.pdf")
A3 = Path("tests/sample/A3-booklet.pdf")


def test_it():
    def f(paths):
        return list(stat_pdf(paths))

    assert f([A4]) == [PathAndCount(A4, 10)]
    assert f([A3]) == [PathAndCount(A3, 4)]
    assert f([A4, A3]) == [PathAndCount(A4, 10), PathAndCount(A3, 4)]
