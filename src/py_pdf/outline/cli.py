import argparse
from pathlib import Path

from py_pdf.utils import new_path_with_timestamp

from .core import (
    get_outline,
    remove_outline,
    set_outline,
)


def cli():
    parser = argparse.ArgumentParser(
        prog="outline",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="cmd")

    cmd_get = subparsers.add_parser("get", help="提取outline")
    cmd_get.add_argument("pdf_file_path", type=Path, help="输入PDF文件路径")

    cmd_set = subparsers.add_parser("set", help="设置outline")
    cmd_set.add_argument("pdf_file_path", type=Path, help="输入PDF文件路径")
    cmd_set.add_argument("outline_file_path", type=Path, help="outline文件路径")
    cmd_set.add_argument(
        "page_offset", type=int, nargs="?", default=0, help="页码偏移量，默认0"
    )

    cmd_rm = subparsers.add_parser("rm", help="删除outline")
    cmd_rm.add_argument("pdf_file_path", type=Path, help="输入PDF文件路径")

    args = parser.parse_args()
    pdf_file_path: Path = args.pdf_file_path

    match args.cmd:
        case "get":
            outline = get_outline(pdf_file_path)
            outline_txt_path = new_path_with_timestamp(pdf_file_path, ".txt")
            if outline_txt_path.exists():
                print(f"overwrite {outline_txt_path}")
            outline_txt_path.write_text(outline, encoding="utf-8")
            print(f"save as\n{outline_txt_path}")
        case "set":
            outline_txt_path: Path = args.outline_file_path
            page_offset: int = args.page_offset
            output_path = new_path_with_timestamp(pdf_file_path)
            set_outline(pdf_file_path, output_path, outline_txt_path, page_offset)
            print(f"save as\n{output_path}")
        case "rm":
            output_path = new_path_with_timestamp(pdf_file_path)
            remove_outline(pdf_file_path, output_path)
            print(f"save as\n{output_path}")
        case _:
            # should not reach here
            parser.print_help()


def main():
    try:
        cli()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
