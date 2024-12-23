import os.path as osp

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont

FONT_DICT = {
    "黑体": "SimHei.ttf",
    "Arial": "arial.ttf",
    "times": "times.ttf",
    "微软雅黑": "msyh.ttc",
    "宋体": "simsun.ttc",
    "隶书": "SIMLI.TTF",
    "楷体": "simkai.ttf",
    "仿宋": "simfang.ttf",
}
for font_name, font_file in FONT_DICT.items():
    pdfmetrics.registerFont(TTFont(font_name, font_file))

DEFAULT_FONT_NAME = "黑体"
DEFAULT_FONT_SIZE = 12


def register_font(font_file: str) -> str:
    name = osp.basename(font_file)
    try:
        pdfmetrics.registerFont(TTFont(name, font_file))
        return name
    except TTFError as e:
        print(e)
        print(f"use default font: {DEFAULT_FONT_NAME}")
        return DEFAULT_FONT_NAME
