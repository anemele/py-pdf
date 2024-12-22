from pathlib import Path

from py_pdf.booklet import make_booklet, split_booklet

VERTICAL = True

this_dir = Path(__file__).parent


def test_it():
    fp = "tests/sample/A3-booklet.pdf"
    fp = split_booklet(fp, this_dir.joinpath("s1.pdf"), VERTICAL)
    fp = split_booklet(fp, fp.with_name("s2.pdf"), VERTICAL)
    fp = split_booklet(fp, fp.with_name("s3.pdf"), VERTICAL)
    fp = make_booklet(fp, fp.with_name("m1.pdf"), VERTICAL)
    fp = make_booklet(fp, fp.with_name("m2.pdf"), VERTICAL)
    fp = make_booklet(fp, fp.with_name("m3.pdf"), VERTICAL)
