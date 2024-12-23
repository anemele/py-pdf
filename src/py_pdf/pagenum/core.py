"""给PDF文件添加页码，添加位置为页尾居中。
默认全文从1开始，按自然数顺序编号。

支持输入配置，格式为： `a-b:A` ，标示从a页到b页编号，a页编号为A，依次类推。
支持多个配置，以逗号分割，格式为： `a-b:A,c-d:C` 。
另外支持文件配置，格式同上，支持以逗号和换行符分割。

自行保证输入合法，本程序不做验证。
"""

import argparse
from pathlib import Path
from typing import Callable

from pypdf import PageObject, PdfReader, PdfWriter

from py_pdf.utils import new_path_with_timestamp

from .config import NumPos, PageRange, default_config, parse_config
from .text import add_text


def _gen_add_pn(
    num_pos: NumPos, num_format: str
) -> Callable[[PageObject, int], PageObject]:
    match num_pos:
        case NumPos.LEFT:

            def add_pn(page: PageObject, num: int) -> PageObject:
                return add_text(page, 3 / 16, 1 / 18, num_format.format(num))
        case NumPos.RIGHT:

            def add_pn(page: PageObject, num: int) -> PageObject:
                return add_text(page, 13 / 16, 1 / 18, num_format.format(num))

        case NumPos.ODD_LEFT:

            def add_pn(page: PageObject, num: int) -> PageObject:
                if num % 2 == 0:
                    return add_text(page, 13 / 16, 1 / 18, num_format.format(num))
                else:
                    return add_text(page, 3 / 16, 1 / 18, num_format.format(num))

        case NumPos.ODD_RIGHT:

            def add_pn(page: PageObject, num: int) -> PageObject:
                if num % 2 == 0:
                    return add_text(page, 3 / 16, 1 / 18, num_format.format(num))
                else:
                    return add_text(page, 13 / 16, 1 / 18, num_format.format(num))

        case NumPos.CENTER:

            def add_pn(page: PageObject, num: int) -> PageObject:
                return add_text(page, 1 / 2, 1 / 18, num_format.format(num))

        case _:
            print(f"Error: invalid num_pos: {num_pos}")

            def add_pn(page: PageObject, num: int) -> PageObject:
                return add_text(page, 1 / 2, 1 / 18, num_format.format(num))

    return add_pn


def add_pagenum(
    input_file: Path | str,
    output_file: Path | str,
    config_str_or_file: str | None = None,
) -> None:
    reader = PdfReader(input_file)
    pages = reader.pages
    writer = PdfWriter()

    if config_str_or_file is not None:
        config = parse_config(config_str_or_file)
    else:
        config = default_config(len(pages))

    add_pn = _gen_add_pn(config.num_pos, config.num_format)

    new_pages = []
    old_range = PageRange(0, 0, 0)
    for new_range in PageRange.parse_range(config.page_range):
        new_pages.extend(pages[old_range.pdf_end : new_range.pdf_start - 1])
        offset = 0
        for i in range(new_range.pdf_start - 1, new_range.pdf_end):
            page = pages[i]
            new_page = add_pn(page, new_range.num_start + offset)
            new_pages.append(new_page)
            offset += 1
        old_range = new_range
    new_pages.extend(pages[old_range.pdf_end :])
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
    parser.add_argument("--range", help="page range, format: a-b:A,c-d:C")
    parser.add_argument("--config-file")

    args = parser.parse_args()
    input_file: Path = args.input_file
    _range: str | None = args.range
    config_file: str | None = args.config_file

    output_file = new_path_with_timestamp(input_file)

    try:
        if _range is not None:
            add_pagenum(input_file, output_file, f"page_range='{_range}'")
        elif config_file is not None:
            add_pagenum(input_file, output_file, config_file)
        else:
            add_pagenum(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
