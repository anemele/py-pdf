import argparse
from pathlib import Path
from typing import Optional

from .outline import (
    get_outline,
    remove_outline,
    reset_outline,
    set_outline,
)


def main():
    parser = argparse.ArgumentParser(
        prog="outline",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_path", type=Path, help="输入PDF文件路径")
    parser.add_argument("--outline-file-path", type=Path, help="outline文件路径")
    parser.add_argument("--page-offset", type=int, default=0, help="页码偏移量")
    cmd_grp = parser.add_mutually_exclusive_group()
    cmd_grp.add_argument("--get", action="store_true", help="提取outline")
    cmd_grp.add_argument("--set", action="store_true", help="设置outline")
    cmd_grp.add_argument("--rm", action="store_true", help="删除outline")
    cmd_grp.add_argument("--rst", action="store_true", help="重置outline")

    args = parser.parse_args()
    input_path: Path = args.input_path
    outline_txt_path: Optional[Path] = args.outline_file_path
    page_offset: int = args.page_offset

    try:
        if args.get:
            get_outline(input_path)
        elif args.set:
            if outline_txt_path is None:
                print("请指定outline文件路径")
                exit()
            set_outline(input_path, outline_txt_path, page_offset)
        elif args.rm:
            remove_outline(input_path)
        elif args.rst:
            if outline_txt_path is None:
                print("请指定outline文件路径")
                exit()
            reset_outline(input_path, outline_txt_path, page_offset)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
