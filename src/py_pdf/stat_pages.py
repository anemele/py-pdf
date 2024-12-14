import argparse
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
    for path in paths:
        if path.is_file():
            res = get_page_num(path)
            file_count += res[0]
            page_count += res[1]
        else:
            for pdffile in path.glob("**/*.pdf"):
                res = get_page_num(pdffile)
                file_count += res[0]
                page_count += res[1]
    return file_count, page_count


def main():
    parser = argparse.ArgumentParser(
        prog=__package__, description="Count pages in PDF files"
    )
    parser.add_argument("path", nargs="+", type=Path, help="Paths to PDF files")
    args = parser.parse_args()
    paths: list[Path] = args.path

    file_count, page_count = stat_pdf(paths)
    print(f"Total files: {file_count}")
    print(f"Total pages: {page_count}")


if __name__ == "__main__":
    main()
