"""
TOML configuration.

```toml
page_range = '1-100:1,150-200:200'
odd_right = true
num_format = '-%d-'

```

"""

import os.path as osp
import re
from dataclasses import dataclass, field

from mashumaro.mixins.toml import DataClassTOMLMixin


@dataclass
class PageRange:
    pdf_start: int
    pdf_end: int
    num_start: int

    @staticmethod
    def parse_range(range_str: str) -> list["PageRange"]:
        """a-b:A,c-d:C
        e-f:E,g-h:G"""
        res = []
        for r in re.findall(r"(\d+)-(\d+):(\d+)", range_str):
            pnc = PageRange(*map(int, r))
            res.append(pnc)
        res.sort(key=lambda x: x.pdf_start)
        return res


@dataclass
class Config(DataClassTOMLMixin):
    page_range: str
    odd_right: bool = field(default=False)
    num_format: str = field(default="%d")


def default_config(end: int) -> Config:
    return Config(page_range=f"1-{end}:1")


def _parse_config(config_str: str) -> Config:
    return Config.from_toml(config_str)


def parse_config(sth: str) -> Config:
    if not osp.exists(sth):
        config = _parse_config(sth)
    else:
        with open(sth, encoding="utf-8") as f:
            config = _parse_config(f.read())
    return config
