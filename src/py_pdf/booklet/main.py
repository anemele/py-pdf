import argparse
import os.path as osp

from .booklet import make_booklet, split_booklet


def main(args=None):
    parser = argparse.ArgumentParser(prog=__package__, description="PDF小册子转换工具")
    parser.add_argument("input_pdf_path", type=str, help="输入PDF文件路径")
    parser.add_argument("-x", "--horizontal", action="store_true", help="横向分割")
    cmd_grp = parser.add_mutually_exclusive_group()
    cmd_grp.add_argument(
        "--make", action="store_true", help="将竖向PDF文档转换为小册子"
    )
    cmd_grp.add_argument(
        "--split", action="store_true", help="将横向PDF小册子分割为文档"
    )

    args = parser.parse_args(args)

    input_pdf_path = args.input_pdf_path
    horizontal = args.horizontal
    output_pdf_path = "_new".join(osp.splitext(input_pdf_path))

    try:
        if args.make:
            make_booklet(input_pdf_path, output_pdf_path, vertical=not horizontal)
        elif args.split:
            split_booklet(input_pdf_path, output_pdf_path, vertical=not horizontal)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
