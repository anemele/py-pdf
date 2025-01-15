"""统计PDF文件数目和页数，支持输入文件和目录。
输入目录时默认搜索所有子目录：`glob: **/*.pdf`
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from pypdf import PdfReader


@dataclass
class PathAndCount:
    path: Path
    count: int


def read_pdf(path: Path) -> Optional[PathAndCount]:
    try:
        reader = PdfReader(path)
        return PathAndCount(path, len(reader.pages))
    except Exception as e:
        print(f"Error reading {path}: {e}")


def stat_pdf(paths: Iterable[Path]) -> Iterable[PathAndCount]:
    def chain_files():
        for path in paths:
            if path.is_file():
                yield path
            else:
                yield from path.glob("**/*.pdf")

    res = filter(None, map(read_pdf, chain_files()))
    return res


def print_result(result: Iterable[PathAndCount]):
    file_count = 0
    page_count = 0
    for item in result:
        file_count += 1
        page_count += item.count
    print(f"Total files: {file_count}")
    print(f"Total pages: {page_count}")


def print_result_verbose(result: Iterable[PathAndCount]):
    file_count = 0
    page_count = 0
    for item in result:
        file_count += 1
        page_count += item.count
        print(f"{item.count:4d}    {item.path}")
    print(f"Total files: {file_count}")
    print(f"Total pages: {page_count}")


def main():
    parser = argparse.ArgumentParser(
        prog=Path(__file__).name.removesuffix(".py"),
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("path", nargs="*", type=Path, help="Paths to PDF files")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show verbose output"
    )
    args = parser.parse_args()
    paths: list[Path] = args.path
    verbose: bool = args.verbose

    if len(paths) == 0:
        paths = [Path.cwd()]

    res = stat_pdf(paths)
    if verbose:
        print_result_verbose(res)
    else:
        print_result(res)


if __name__ == "__main__":
    main()
