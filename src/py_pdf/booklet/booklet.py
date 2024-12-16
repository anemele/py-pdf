import copy
from pathlib import Path

from pypdf import PageObject, PdfReader, PdfWriter


def resort_to_booklet(
    pages: list[PageObject], blank_page: PageObject
) -> list[PageObject]:
    """将PDF页面从自然顺序转换为小册子顺序。
    1, 2, 3, 4, 5, 6, 7, 8
    ->
    8, 1, 2, 7, 6, 3, 4, 5
    """
    pages.extend([blank_page] * ((4 - len(pages) % 4) % 4))
    res = []
    left = 0
    right = len(pages) - 1
    for i in range(len(pages) // 2):
        if i % 2 == 0:
            res.append(pages[right])
            res.append(pages[left])
        else:
            res.append(pages[left])
            res.append(pages[right])
        left += 1
        right -= 1
    return res


def merge_two_pages(page1: PageObject, page2: PageObject, vertical: bool) -> PageObject:
    """两个页面尺寸应该相同"""
    page1 = copy.deepcopy(page1)
    page2 = copy.deepcopy(page2)

    width = page1.mediabox.width
    height = page1.mediabox.height

    if vertical:
        res = PageObject.create_blank_page(None, 2 * width, height)
        res.merge_translated_page(page1, -page1.mediabox.left, -page1.mediabox.bottom)
        res.merge_translated_page(
            page2, width - page2.mediabox.left, -page2.mediabox.bottom
        )
    else:
        res = PageObject.create_blank_page(None, width, 2 * height)
        res.merge_translated_page(
            page1, -page1.mediabox.left, height - page1.mediabox.bottom
        )
        res.merge_translated_page(page2, -page2.mediabox.left, -page2.mediabox.bottom)
    return res


def make_booklet(
    input_pdf_path: Path | str, output_pdf_path: Path | str, vertical: bool = True
) -> Path:
    reader = PdfReader(input_pdf_path)

    pages = list(reader.pages)
    blank_page = PageObject.create_blank_page(
        None, pages[0].mediabox.width, pages[0].mediabox.height
    )
    pages = resort_to_booklet(pages, blank_page)

    # 此时页面数量为 4 的倍数，迭代器不会 StopIteration
    pages = iter(pages)
    pages = [merge_two_pages(i, next(pages), vertical) for i in pages]

    writer = PdfWriter()
    # writer.add_page(pages[0])
    # writer.add_page(pages[1])
    # writer.add_page(merge_two_pages(pages[0], pages[1], vertical))
    for page in pages:
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)
    writer.close()
    reader.close()

    return Path(output_pdf_path)


def resort_from_booklet(pages: list[PageObject]) -> list[PageObject]:
    """将PDF页面从小册子顺序转换为自然顺序。
    页面数目必须是 4 的倍数。
    8, 1, 2, 7, 6, 3, 4, 5
    ->
    1, 2, 3, 4, 5, 6, 7, 8
    """
    if len(pages) % 4 != 0:
        raise ValueError("页面数目必须是 4 的倍数")

    left = []
    right = []
    for i in range(len(pages) // 2):
        if i % 2 == 0:
            left.append(pages[2 * i])
            right.append(pages[2 * i + 1])
        else:
            left.append(pages[2 * i + 1])
            right.append(pages[2 * i])

    return right + left[::-1]


def crop_page(page: PageObject, vertical: bool) -> tuple[PageObject, PageObject]:
    width = page.mediabox.width
    height = page.mediabox.height

    page1 = copy.deepcopy(page)
    page2 = copy.deepcopy(page)

    # PDF 坐标系原点在左下角，所以y轴向上为正
    # PDF 的页面比较特殊，裁剪结果不是真实的裁剪，而是显示的裁剪。
    # 因此，裁剪方法要设置相对坐标，而非绝对值。
    if vertical:
        half_width = width / 2
        page1.mediabox.right -= half_width
        page2.mediabox.left += half_width
    else:
        half_height = height / 2
        page1.mediabox.bottom += half_height
        page2.mediabox.top -= half_height

    return page1, page2


def split_booklet(
    input_pdf_path: Path | str, output_pdf_path: Path | str, vertical: bool = True
) -> Path:
    reader = PdfReader(input_pdf_path)

    pages = [p for page in reader.pages for p in crop_page(page, vertical)]

    pages = resort_from_booklet(pages)

    writer = PdfWriter()
    for page in pages:
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)
    writer.close()
    reader.close()

    return Path(output_pdf_path)
