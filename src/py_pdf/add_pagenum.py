"""给PDF文件添加页码，添加位置为页尾居中。
默认全文从1开始，按自然数顺序编号。

支持输入配置，格式为： `a-b:A` ，标示从a页到b页编号，a页编号为A，依次类推。
支持多个配置，以逗号分割，格式为： `a-b:A,c-d:C` 。
另外支持文件配置，格式同上，支持以逗号和换行符分割。

自行保证输入合法，本程序不做验证。
"""

import argparse
import io
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from .utils import new_path_with_timestamp

FONT_DICT = dict(
    SimHei="SimHei.ttf",
    Times="times.ttf",
)
for font_name, font_file in FONT_DICT.items():
    pdfmetrics.registerFont(TTFont(font_name, font_file))


def add_text(page: PageObject, text: str) -> PageObject:
    new_page = PageObject.create_blank_page(
        None, page.mediabox.width, page.mediabox.height
    )

    packet = io.BytesIO()
    canvas_draw = Canvas(
        packet, pagesize=(new_page.mediabox.width, new_page.mediabox.height)
    )
    canvas_draw.setFont("Times", 16)
    canvas_draw.drawString(
        new_page.mediabox.width / 2,
        new_page.mediabox.height / 18,
        text,
    )
    canvas_draw.save()

    text_page = PdfReader(packet).pages[0]

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


@dataclass
class PageNumConfig:
    pdf_start: int
    pdf_end: int
    display_start: int


def parse_config(config: str) -> list[PageNumConfig]:
    """a-b:A,c-d:C
    e-f:E,g-h:G"""
    res = []
    for r in re.findall(r"(\d+)-(\d+):(\d+)", config):
        pnc = PageNumConfig(*map(int, r))
        res.append(pnc)
    return res


def add_pagenum(
    input_file: Path | str, output_file: Path | str, config_str: str | None = None
) -> None:
    reader = PdfReader(input_file)
    writer = PdfWriter()

    if config_str is None:
        for i, page in enumerate(reader.pages, start=1):
            new_page = add_text(page, str(i))
            writer.add_page(new_page)
    else:
        pages = reader.pages
        config_list = parse_config(config_str)
        config_list.sort(key=lambda x: x.pdf_start)
        new_pages = []
        old_config = PageNumConfig(0, 0, 0)
        for config in config_list:
            new_pages.extend(pages[old_config.pdf_end : config.pdf_start - 1])
            offset = 0
            for i in range(config.pdf_start - 1, config.pdf_end):
                page = pages[i]
                new_page = add_text(page, str(config.display_start + offset))
                new_pages.append(new_page)
                offset += 1
            old_config = config
        new_pages.extend(pages[old_config.pdf_end :])
        for page in new_pages:
            writer.add_page(page)

    with open(output_file, "wb") as fp:
        writer.write(fp)

    writer.close()
    reader.close()


def main():
    parser = argparse.ArgumentParser(
        prog="addpn",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_file", type=Path, help="input PDF file")
    parser.add_argument(
        "-c", "--config", help="page number config, format: a-b:A[,c-d:C]"
    )
    parser.add_argument("--config-file", help="page number config file")

    args = parser.parse_args()
    input_file: Path = args.input_file
    config_str: str | None = args.config
    config_file: str | None = args.config_file

    output_file = new_path_with_timestamp(input_file)

    try:
        if config_str is not None:
            add_pagenum(input_file, output_file, config_str)
        elif config_file is not None:
            with open(config_file, "r") as fp:
                config_str = fp.read()
            add_pagenum(input_file, output_file, config_str)
        else:
            add_pagenum(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
