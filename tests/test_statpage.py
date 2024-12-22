from pathlib import Path

from py_pdf.statpage import stat_pdf

A4 = Path("tests/sample/A4.pdf")
A3 = Path("tests/sample/A3-booklet.pdf")


def test_it():
    assert stat_pdf([A4]) == (1, 10)
    assert stat_pdf([A3]) == (1, 4)
    assert stat_pdf([A4, A3]) == (2, 14)
