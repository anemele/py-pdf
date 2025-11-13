from pathlib import Path
from typing import Callable

from pypdf import PageObject, PdfReader, PdfWriter

from .config import Config, NumMode, PageRange, parse_config
from .text import add_text


def _gen_add_pn(config: Config) -> Callable[[PageObject, int], PageObject]:
    def get_x_pos(num: int) -> float:
        x = config.num_pos.x
        match config.num_pos.mode:
            case NumMode.RIGHT1:
                if num % 2 == 0:
                    return 1 - x
                else:
                    return x
            case NumMode.RIGHT2:
                if num % 2 == 0:
                    return x
                else:
                    return 1 - x
            case _:
                return x

    def add_pn(page: PageObject, num: int) -> PageObject:
        return add_text(
            page,
            get_x_pos(num),
            config.num_pos.y,
            config.num_fmt.format(num),
            config.font_name,
            config.font_size,
        )

    return add_pn


def add_pagenum(
    input_file: Path | str, output_file: Path | str, config_str: str
) -> None:
    reader = PdfReader(input_file)
    pages = reader.pages
    writer = PdfWriter()

    config = parse_config(config_str)
    add_pn = _gen_add_pn(config)

    if config.page_range == "":
        for i, page in enumerate(pages, 1):
            new_page = add_pn(page, i)
            writer.add_page(new_page)
    else:
        new_pages = list[PageObject]()
        old_range = PageRange(0, 0, 0)
        for new_range in PageRange.parse_range(config.page_range):
            new_pages.extend(pages[old_range.pdf_end : new_range.pdf_start - 1])
            offset = 0
            for i in range(new_range.pdf_start - 1, new_range.pdf_end):
                page = pages[i]
                new_page = add_pn(page, new_range.num_start + offset)
                new_pages.append(new_page)
                offset += 1
            old_range = new_range
        new_pages.extend(pages[old_range.pdf_end :])
        for page in new_pages:
            writer.add_page(page)

    with open(output_file, "wb") as fp:
        writer.write(fp)

    writer.close()
    reader.close()
