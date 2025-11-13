"""PDF 文件添加页码。

程序会自动检测配置文件，如果不存在则会生成，按需修改后再次运行即可。
"""

import argparse
from pathlib import Path

from py_pdf._com import new_path_with_timestamp

from .config import cfg_template
from .core import add_pagenum


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="addpn",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_file", type=Path, help="input PDF file")

    args = parser.parse_args()
    input_file: Path = args.input_file

    cfg_file_path = Path("config.toml")
    if not cfg_file_path.exists():
        cfg_file_path.write_text(cfg_template, encoding="utf-8")
        print(f"Config and then run again: {cfg_file_path}")
        return 1
    config_str = cfg_file_path.read_text(encoding="utf-8")
    output_file = new_path_with_timestamp(input_file)

    try:
        add_pagenum(input_file, output_file, config_str)
    except Exception as e:
        print(f"Error: {e}")

    return 0


if __name__ == "__main__":
    exit(main())
