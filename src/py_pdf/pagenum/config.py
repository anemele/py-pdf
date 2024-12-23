import os.path as osp
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Optional

import tomllib
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
        res: list[PageRange] = []
        for r in re.findall(r"(\d+)-(\d+):(\d+)", range_str):
            pnc = PageRange(*map(int, r))
            res.append(pnc)
        res.sort(key=lambda x: x.pdf_start)
        return res


class NumPos(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    ODD_LEFT = "odd-left"
    ODD_RIGHT = "odd-right"


@dataclass
class Config(DataClassTOMLMixin):
    page_range: Optional[str] = field(default=None)
    num_pos: NumPos = field(default=NumPos.CENTER)
    num_fmt: str = field(default="{:d}")
    font_name: str = field(default=DEFAULT_FONT_NAME)
    font_size: int = field(default=DEFAULT_FONT_SIZE)

    def __post_init__(self):
        if self.font_name not in FONT_DICT:
            self.font_name = register_font(self.font_name)


def default_config() -> Config:
    return Config()


def _parse_config(config_str: str) -> Config:
    def replace_hyphen_with_underscore(s: str) -> dict[str, Any]:
        sth = tomllib.loads(s)
        for k in tuple(sth.keys()):
            if "-" in k:
                sth[k.replace("-", "_")] = sth.pop(k)
        return sth

    return Config.from_toml(config_str, replace_hyphen_with_underscore)


def parse_config(sth: str) -> Config:
    if not osp.exists(sth):
        config = _parse_config(sth)
    else:
        with open(sth, encoding="utf-8") as f:
            config = _parse_config(f.read())
    return config
