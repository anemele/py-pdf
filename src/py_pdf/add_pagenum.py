"""给PDF文件添加页码，添加位置为页尾居中。
默认全文从1开始，按自然数顺序编号。

支持输入配置，格式为： `a-b:A` ，标示从a页到b页编号，a页编号为A，依次类推。
支持多个配置，以逗号分割，格式为： `a-b:A,c-d:C` 。
另外支持文件配置，格式同上，支持以逗号和换行符分割。

自行保证输入合法，本程序不做验证。
"""

import argparse
import io
import os
import re
from dataclasses import dataclass

from pypdf import PageObject, PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

pdfmetrics.registerFont(TTFont("SimHei", "SimHei.ttf"))
pdfmetrics.registerFont(TTFont("Times", "times.ttf"))


def add_text(page: PageObject, text: str) -> None:
    packet = io.BytesIO()
    canvas_draw = Canvas(packet, pagesize=(page.mediabox.width, page.mediabox.height))
    canvas_draw.setFont("Times", 16)
    canvas_draw.drawString(page.mediabox.width / 2, page.mediabox.height / 18, text)
    canvas_draw.save()

    text_page = PdfReader(packet).pages[0]
    page.merge_page(text_page)


@dataclass
class PageNumConfig:
    pdf_start: int
    pdf_end: int
    display_start: int


def parse_config(config: str) -> list[PageNumConfig]:
    """a-b:A-B"""
    res = []
    for r in re.findall(r"(\d+)-(\d+):(\d+)", config):
        pnc = PageNumConfig(*map(int, r))
        res.append(pnc)
    return res


def add_pagenum(
    input_file: str, output_file: str, config_str: str | None = None
) -> None:
    reader = PdfReader(input_file)
    writer = PdfWriter()

    pages = reader.pages
    if config_str is not None:
        config_list = parse_config(config_str)
        for config in config_list:
            offset = 0
            for i in range(config.pdf_start - 1, config.pdf_end):
                page = pages[i]
                add_text(page, str(config.display_start + offset))
                offset += 1
    else:
        for i, page in enumerate(pages):
            add_text(page, str(i + 1))

    for page in pages:
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
    parser.add_argument("input_file", help="input PDF file")
    parser.add_argument(
        "-c", "--config", help="page number config, format: a-b:A[,c-d:C]"
    )
    parser.add_argument("--config-file", help="page number config file")
    parser.print_help
    args = parser.parse_args()
    input_file = args.input_file
    config_str = args.config
    config_file = args.config_file

    output_file = "_new".join(os.path.splitext(input_file))

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
