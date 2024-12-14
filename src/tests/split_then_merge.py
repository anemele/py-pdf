from pathlib import Path

from py_pdf.booklet import make_booklet, split_booklet

VERTICAL = True


def do_test(fp: Path):
    fp = split_booklet(fp, fp.with_name("s1.pdf"), VERTICAL)
    fp = split_booklet(fp, fp.with_name("s2.pdf"), VERTICAL)
    fp = split_booklet(fp, fp.with_name("s3.pdf"), VERTICAL)
    fp = make_booklet(fp, fp.with_name("m1.pdf"), VERTICAL)
    fp = make_booklet(fp, fp.with_name("m2.pdf"), VERTICAL)
    fp = make_booklet(fp, fp.with_name("m3.pdf"), VERTICAL)


if __name__ == "__main__":
    import sys

    do_test(Path(sys.argv[1]))
