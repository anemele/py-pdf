import io

from pypdf import PageObject, PdfReader, Transformation
from reportlab.pdfgen.canvas import Canvas


def _create_text_page(
    width: float,
    height: float,
    xrate: float,
    yrate: float,
    text: str,
    font_name: str,
    font_size: int,
) -> PageObject:
    """
    `xrate` and `yrate` are to locate the position of the text on the page,
    where is (0, 0) is the left-bottom corner of the page, and (1, 1) is the right-top corner.
    """
    packet = io.BytesIO()
    canvas_draw = Canvas(packet, pagesize=(width, height))
    canvas_draw.setFont(font_name, font_size)
    canvas_draw.drawCentredString(width * xrate, height * yrate, text)
    canvas_draw.save()

    text_page = PdfReader(packet).pages[0]
    return text_page


def add_text(
    page: PageObject,
    xrate: float,
    yrate: float,
    text: str,
    font_name: str,
    font_size: int,
) -> PageObject:
    text_page = _create_text_page(
        page.mediabox.width,
        page.mediabox.height,
        xrate,
        yrate,
        text,
        font_name,
        font_size,
    )

    new_page = PageObject.create_blank_page(
        None, page.mediabox.width, page.mediabox.height
    )
    new_page.merge_transformed_page(
        page, Transformation().translate(-page.mediabox.left, -page.mediabox.bottom)
    )
    new_page.merge_transformed_page(
        text_page,
        Transformation().translate(
            -text_page.mediabox.left, -text_page.mediabox.bottom
        ),
    )

    return new_page
