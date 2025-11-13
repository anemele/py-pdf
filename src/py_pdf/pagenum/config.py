import re
import tomllib
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from mashumaro.mixins.toml import DataClassTOMLMixin

from .font import DEFAULT_FONT_NAME, DEFAULT_FONT_SIZE, FONT_DICT, register_font


@dataclass
class PageRange:
    pdf_start: int
    pdf_end: int
    num_start: int

    @staticmethod
    def parse_range(range_str: str) -> list["PageRange"]:
        """a-b:A,c-d:C
        e-f:E,g-h:G"""
        res = list[PageRange]()
        for r in re.findall(r"(\d+)-(\d+):(\d+)", range_str):
            pnc = PageRange(*map(int, r))
            res.append(pnc)
        res.sort(key=lambda x: x.pdf_start)
        return res


class NumMode(StrEnum):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    RIGHT1 = "right1"  # 奇数页码居右
    RIGHT2 = "right2"  # 偶数页码居右


@dataclass
class NumPos:
    x: float = field(default=-1)
    y: float = field(default=-1)
    mode: NumMode = field(default=NumMode.CENTER)

    def __post_init__(self):
        def check_xy() -> bool:
            return 0 <= self.x <= 1 and 0 <= self.y <= 1

        def default_xy() -> tuple[float, float]:
            y = 1 / 16
            match self.mode:
                case NumMode.CENTER:
                    x = 1 / 2
                case NumMode.LEFT:
                    x = 3 / 16
                case NumMode.RIGHT | NumMode.RIGHT1 | NumMode.RIGHT2:
                    # first x for right1 and right2
                    x = 13 / 16
            return x, y

        if not check_xy():
            self.x, self.y = default_xy()


@dataclass
class Config(DataClassTOMLMixin):
    page_range: str = field(default="")
    num_pos: NumPos = field(default_factory=NumPos)
    num_fmt: str = field(default="{:d}")
    font_name: str = field(default=DEFAULT_FONT_NAME)
    font_size: int = field(default=DEFAULT_FONT_SIZE)

    def __post_init__(self):
        if self.font_name not in FONT_DICT:
            self.font_name = register_font(self.font_name)


cfg_template = """\
# 默认全文档添加页码，从 1 开始，递增编号，位置为页尾居中。
# 页码范围格式为 a-b:A 表示从a到b标注页码，a 对应 A
# 可以写多个页码范围，用空格或者逗号隔开，如 a-b:A,c-d:C
page_range = ""
# 页码格式，可以添加一些修饰，如 -{:d}-  第{:d}页
num_fmt = "{:d}"

font_name = "Times New Roman"
font_size = 16

# 页码位置，坐标原点在左下角
[num_pos]
# 从左到右 1/2 的位置
x = 0.5
# 从下到上 1/16 的位置
y = 0.0625
# 五种模式：center left right right1 right2
# 这五种模式在缺省 x 时可以提供默认值
# 另外 right1 奇数页码居右，righ2 偶数页码居右
mode = "center"
"""


def parse_config(config_str: str) -> Config:
    def replace_hyphen_with_underscore(s: str) -> dict[str, Any]:
        sth = tomllib.loads(s)
        for k in tuple(sth.keys()):
            if "-" in k:
                sth[k.replace("-", "_")] = sth.pop(k)
        return sth

    return Config.from_toml(config_str, replace_hyphen_with_underscore)
