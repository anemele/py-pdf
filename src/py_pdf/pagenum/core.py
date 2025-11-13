from pathlib import Path
from typing import Sequence

from pypdf import PageObject, PdfReader, PdfWriter

from .config import Config, NumMode, PageRange, parse_config
from .text import add_text


def _add_pagenum(
    config: Config, page_range: Sequence[PageRange], pages: Sequence[PageObject]
) -> list[PageObject]:
    def gen_i():
        x = config.num_pos.x

        if config.num_pos.mode == NumMode.STAGGER:

            def f():
                while True:
                    yield x
                    yield 1 - x

        else:

            def f():
                while True:
                    yield x

        for r in page_range:
            g = f()
            a = 0
            for i in range(r.pdf_start - 1, r.pdf_end):
                yield i, r.num_start + a, next(g)
                a += 1

    inx = {i: (num, x) for i, num, x in gen_i()}
    ret = []
    for i, page in enumerate(pages):
        if i not in inx:
            ret.append(page)
            continue
        num, x = inx[i]
        page = add_text(
            page,
            x,
            config.num_pos.y,
            config.num_fmt.format(num),
            config.font_name,
            config.font_size,
        )
        ret.append(page)

    return ret


def add_pagenum(
    input_file: Path | str, output_file: Path | str, config_str: str
) -> None:
    reader = PdfReader(input_file)
    pages = reader.pages

    config = parse_config(config_str)

    if config.page_range == "":
        page_range = [PageRange(0, len(pages) - 1, 1)]
    else:
        page_range = PageRange.parse_range(config.page_range)

    pages = _add_pagenum(config, page_range, pages)

    writer = PdfWriter()
    for page in pages:
        writer.add_page(page)

    with open(output_file, "wb") as fp:
        writer.write(fp)

    writer.close()
    reader.close()
