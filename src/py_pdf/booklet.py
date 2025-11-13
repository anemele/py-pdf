"""PDF小册子转换工具。

可以将正常顺序的文档转换成小册子，也可以将小册子分割并重新排序成正常顺序的文档。
"""

import argparse
from pathlib import Path

from pypdf import PageObject, PdfReader, PdfWriter

from ._com import (
    crop_page,
    merge_two_pages,
    new_path_with_timestamp,
    sort_from_booklet,
    sort_to_booklet,
)


def make_booklet(
    input_pdf_path: Path | str, output_pdf_path: Path | str, vertical: bool = True
) -> Path:
    reader = PdfReader(input_pdf_path)

    pages = list(reader.pages)
    if (r := len(pages) % 4) != 0:
        blank_page = PageObject.create_blank_page(
            None, pages[0].mediabox.width, pages[0].mediabox.height
        )
        pages.extend([blank_page] * (4 - r))
    pages = sort_to_booklet(pages)

    # 此时页面数量为 4 的倍数，迭代器不会 StopIteration
    pages = iter(pages)
    pages = [merge_two_pages(i, next(pages), vertical) for i in pages]

    writer = PdfWriter()
    # writer.add_page(pages[0])
    # writer.add_page(pages[1])
    # writer.add_page(merge_two_pages(pages[0], pages[1], vertical))
    for page in pages:
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)
    writer.close()
    reader.close()

    return Path(output_pdf_path)


def split_booklet(
    input_pdf_path: Path | str, output_pdf_path: Path | str, vertical: bool = True
) -> Path:
    reader = PdfReader(input_pdf_path)

    pages = [p for page in reader.pages for p in crop_page(page, vertical)]

    pages = sort_from_booklet(pages)

    writer = PdfWriter()
    for page in pages:
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)
    writer.close()
    reader.close()

    return Path(output_pdf_path)


def main():
    parser = argparse.ArgumentParser(
        prog=Path(__file__).name.removesuffix(".py"),
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_pdf_path", type=Path, help="输入PDF文件路径")
    parser.add_argument("-x", "--horizontal", action="store_true", help="横向分割/合并")
    cmd_grp = parser.add_mutually_exclusive_group()
    cmd_grp.add_argument("--make", action="store_true", help="将PDF文档转换为小册子")
    cmd_grp.add_argument("--split", action="store_true", help="将PDF小册子分割为文档")

    args = parser.parse_args()

    input_pdf_path: Path = args.input_pdf_path
    horizontal: bool = args.horizontal
    output_pdf_path = new_path_with_timestamp(input_pdf_path)

    try:
        if args.make:
            make_booklet(input_pdf_path, output_pdf_path, vertical=not horizontal)
        elif args.split:
            split_booklet(input_pdf_path, output_pdf_path, vertical=not horizontal)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
