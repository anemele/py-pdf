"""PDF试卷转换工具。

可以将正常顺序的文档转换成试卷，也可以将试卷分割成正常顺序的文档。
"""
# 试卷实际上就是多页合印，与小册子不同之处主要在于无需重排页面顺序。

import argparse
import os.path as osp
from pathlib import Path

from pypdf import PageObject, PdfReader, PdfWriter

from .common import crop_page, merge_two_pages
from .utils import new_path_with_timestamp


def make_paper(
    input_pdf_path: Path | str, output_pdf_path: Path | str, vertical: bool = True
) -> Path:
    reader = PdfReader(input_pdf_path)

    pages = list(reader.pages)
    if len(pages) % 2 != 0:
        blank_page = PageObject.create_blank_page(
            None, pages[0].mediabox.width, pages[0].mediabox.height
        )
        pages.append(blank_page)

    # 此时页面数量为 2 的倍数，迭代器不会 StopIteration
    pages = iter(pages)
    new_pages = (merge_two_pages(i, next(pages), vertical) for i in pages)

    writer = PdfWriter()
    for page in new_pages:
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)
    writer.close()
    reader.close()

    return Path(output_pdf_path)


def split_paper(
    input_pdf_path: Path | str, output_pdf_path: Path | str, vertical: bool = True
) -> Path:
    reader = PdfReader(input_pdf_path)

    pages = (p for page in reader.pages for p in crop_page(page, vertical))

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
        prog=osp.basename(__file__).removesuffix(".py"),
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_pdf_path", type=Path, help="输入PDF文件路径")
    parser.add_argument("-x", "--horizontal", action="store_true", help="横向分割/合并")
    cmd_grp = parser.add_mutually_exclusive_group()
    cmd_grp.add_argument("--make", action="store_true", help="将PDF文档转换为试卷")
    cmd_grp.add_argument("--split", action="store_true", help="将PDF试卷分割为文档")

    args = parser.parse_args()

    input_pdf_path: Path = args.input_pdf_path
    horizontal: bool = args.horizontal
    output_pdf_path = new_path_with_timestamp(input_pdf_path)

    try:
        if args.make:
            make_paper(input_pdf_path, output_pdf_path, vertical=not horizontal)
        elif args.split:
            split_paper(input_pdf_path, output_pdf_path, vertical=not horizontal)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
