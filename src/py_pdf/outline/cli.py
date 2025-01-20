import argparse
from pathlib import Path
from typing import Optional

from py_pdf.utils import new_path_with_timestamp

from .outline import (
    get_outline,
    remove_outline,
    set_outline,
)


def main():
    parser = argparse.ArgumentParser(
        prog="outline",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("pdf_file_path", type=Path, help="输入PDF文件路径")
    parser.add_argument(
        "outline_file_path", nargs="?", type=Path, help="outline文件路径"
    )
    parser.add_argument(
        "page_offset", nargs="?", type=int, default=0, help="页码偏移量"
    )
    cmd_grp = parser.add_mutually_exclusive_group(required=True)
    cmd_grp.add_argument("--get", action="store_true", help="提取outline")
    cmd_grp.add_argument("--set", action="store_true", help="设置outline")
    cmd_grp.add_argument("--rm", action="store_true", help="删除outline")

    args = parser.parse_args()
    pdf_file_path: Path = args.pdf_file_path
    outline_txt_path: Optional[Path] = args.outline_file_path
    page_offset: int = args.page_offset

    try:
        if args.get:
            outline_txt_path = new_path_with_timestamp(pdf_file_path, ".txt")
            get_outline(pdf_file_path, outline_txt_path)
        elif args.set:
            if outline_txt_path is None:
                print("请指定outline文件路径")
                return
            output_path = new_path_with_timestamp(pdf_file_path)
            set_outline(pdf_file_path, output_path, outline_txt_path, page_offset)
        elif args.rm:
            output_path = new_path_with_timestamp(pdf_file_path)
            remove_outline(pdf_file_path, output_path)
        else:
            # should not reach here
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
