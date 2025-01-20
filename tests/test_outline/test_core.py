from pathlib import Path

from py_pdf.outline.core import get_outline, remove_outline, set_outline

this_dir = Path(__file__).parent


def test_all():
    pdf_path = Path("tests/sample/outline.pdf")
    outline_path = Path("tests/sample/outline.txt")

    assert get_outline(pdf_path) == ""

    output_path = this_dir / "output.pdf"
    set_outline(
        pdf_path,
        output_path,
        outline_path,
        0,
    )
    assert (
        get_outline(output_path).strip()
        == outline_path.read_text(encoding="utf-8").strip()
    )

    output_path2 = this_dir / "output2.pdf"
    remove_outline(output_path, output_path2)
    assert get_outline(output_path2) == ""
