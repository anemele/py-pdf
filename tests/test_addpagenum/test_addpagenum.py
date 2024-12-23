from pathlib import Path

from py_pdf.pagenum import add_pagenum

this_dir = Path(__file__).parent


def test_1():
    input_file = "tests/sample/A4.pdf"
    output_file = this_dir / "test_1.pdf"
    add_pagenum(input_file, output_file)


def test_2():
    input_file = "tests/sample/A4.pdf"
    output_file = this_dir / "test_2.pdf"
    add_pagenum(input_file, output_file, "page_range='3-8:10'")


def test_3():
    input_file = "tests/sample/A4.pdf"
    output_file = this_dir / "test_3.pdf"
    config_file = this_dir / "config_3.toml"
    add_pagenum(input_file, output_file, str(config_file))


def test_4():
    input_file = "tests/sample/A4.pdf"
    output_file = this_dir / "test_4.pdf"
    config_file = this_dir / "config_4.toml"
    add_pagenum(input_file, output_file, str(config_file))


def test_5():
    input_file = "tests/sample/A4.pdf"
    output_file = this_dir / "test_5.pdf"
    config_file = this_dir / "config_5.toml"
    add_pagenum(input_file, output_file, str(config_file))


def test_6():
    input_file = "tests/sample/A4.pdf"
    output_file = this_dir / "test_6.pdf"
    config_file = this_dir / "config_6.toml"
    add_pagenum(input_file, output_file, str(config_file))


def test_7():
    input_file = "tests/sample/A4.pdf"
    output_file = this_dir / "test_7.pdf"
    config_file = this_dir / "config_7.toml"
    add_pagenum(input_file, output_file, str(config_file))


def test_8():
    input_file = "tests/sample/A4.pdf"
    output_file = this_dir / "test_8.pdf"
    config_file = this_dir / "config_8.toml"
    add_pagenum(input_file, output_file, str(config_file))
