import os.path as osp
from typing import Optional

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont

FONT_DICT = {
    "黑体": "SimHei.ttf",
    "宋体": "simsun.ttc",
    "仿宋": "simfang.ttf",
    "楷体": "simkai.ttf",
    "隶书": "SIMLI.TTF",
    "Arial": "arial.ttf",
    "Times New Roman": "times.ttf",
    "Verdana": "verdana.ttf",
    "Courier New": "cour.ttf",
}
DEFAULT_FONT_NAME = "Times New Roman"
DEFAULT_FONT_SIZE = 16


def register_font(font_file: str, font_name: Optional[str] = None) -> str:
    if font_name is None:
        font_name = osp.basename(font_file)
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_file))
        return font_name
    except TTFError as e:
        print(e)
        print(f"use default font: {DEFAULT_FONT_NAME}")
        return DEFAULT_FONT_NAME


for font_name, font_file in FONT_DICT.items():
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_file))
    except TTFError:
        pass
