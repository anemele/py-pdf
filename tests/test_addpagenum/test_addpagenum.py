from pathlib import Path

from py_pdf.pagenum.config import cfg_template
from py_pdf.pagenum.core import add_pagenum

this_dir = Path(__file__).parent


def test_default_config():
    add_pagenum("tests/sample/A4.pdf", this_dir / "test_1.pdf", cfg_template)


def test_config_by_string():
    add_pagenum("tests/sample/A4.pdf", this_dir / "test_2.pdf", "page_range='3-8:10'")


def test_config_by_file():
    add_pagenum(
        "tests/sample/A4.pdf",
        this_dir / "test_3.pdf",
        (this_dir / "config.toml").read_text(encoding="utf-8"),
    )


def test_4():
    add_pagenum(
        "tests/sample/A4.pdf",
        this_dir / "test_4.pdf",
        """num-pos = { mode = 'right1' }
num-fmt = '-{:d}-'
""",
    )


def test_5():
    add_pagenum(
        "tests/sample/A4.pdf",
        this_dir / "test_5.pdf",
        """num-pos = { mode = 'right2' }
num-fmt = '-{:d}-'
""",
    )


def test_6():
    add_pagenum(
        "tests/sample/A4.pdf",
        this_dir / "test_6.pdf",
        """num-pos = { mode = 'right2' }
num-fmt = '第{:^3d}页'
font-name = '楷体'
font-size = 12
""",
    )


def test_7():
    add_pagenum(
        "tests/sample/A4.pdf",
        this_dir / "test_7.pdf",
        """num-pos = { mode = 'right2' }
num-fmt = 'no.{:d}'
font-name = '未知'
font-size = 12
""",
    )


def test_8():
    add_pagenum(
        "tests/sample/A4.pdf",
        this_dir / "test_8.pdf",
        r"""num-pos = { mode = 'right2' }
num-fmt = '第{:^3d}页'
font-name = 'C:\Windows\Fonts\HGBTH_CNKI.TTF'
font-size = 12
""",
    )


def test_9():
    add_pagenum(
        "tests/sample/A4.pdf",
        this_dir / "test_9.pdf",
        """num-pos = { x=0.0625, y=0.9375, mode = 'right2' }""",
    )
