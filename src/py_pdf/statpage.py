"""统计PDF文件数目和页数，支持输入文件和目录，支持 glob 。"""

import argparse
import os.path as osp
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


def get_page_num(path: Path) -> tuple[int, int]:
    try:
        reader = PdfReader(path)
        return 1, len(reader.pages)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return 0, 0


def stat_pdf(paths: Iterable[Path]) -> tuple[int, int]:
    file_count = 0
    page_count = 0

    def chain_files():
        for path in paths:
            if path.is_file():
                yield path
            else:
                yield from path.glob("**/*.pdf")

    for file in chain_files():
        res = get_page_num(file)
        file_count += res[0]
        page_count += res[1]

    return file_count, page_count


def main():
    parser = argparse.ArgumentParser(
        prog=osp.basename(__file__).removesuffix(".py"),
        description=__doc__,
    )
    parser.add_argument("path", nargs="+", type=Path, help="Paths to PDF files")
    args = parser.parse_args()
    paths: list[Path] = args.path

    file_count, page_count = stat_pdf(paths)
    print(f"Total files: {file_count}")
    print(f"Total pages: {page_count}")


if __name__ == "__main__":
    main()
