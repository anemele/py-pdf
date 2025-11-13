import copy
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence, TypeVar

from pypdf import PageObject, Transformation

T = TypeVar("T")


def new_path_with_timestamp(path: Path, ext: Optional[str] = None) -> Path:
    now = f"{datetime.now():_%y%m%d_%H%M%S}"
    stem = path.stem
    rematch = re.search(r"_\d{6}_\d{6}$", stem)
    if rematch is not None:
        stem = stem[: rematch.start()]
    ext = ext or path.suffix
    return path.with_name(f"{stem}{now}{ext}")


def sort_to_booklet(pages: Sequence[T]) -> Sequence[T]:
    """将PDF页面从自然顺序转换为小册子顺序。
    页面数目必须是 4 的倍数。
    1, 2, 3, 4, 5, 6, 7, 8
    ->
    8, 1, 2, 7, 6, 3, 4, 5
    """
    if len(pages) % 4 != 0:
        raise ValueError("页面数目必须是 4 的倍数")

    res = list[T]()
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


def sort_from_booklet(pages: Sequence[T]) -> Sequence[T]:
    """将PDF页面从小册子顺序转换为自然顺序。
    页面数目必须是 4 的倍数。
    8, 1, 2, 7, 6, 3, 4, 5
    ->
    1, 2, 3, 4, 5, 6, 7, 8
    """
    if len(pages) % 4 != 0:
        raise ValueError("页面数目必须是 4 的倍数")

    left = list[T]()
    right = list[T]()
    for i in range(len(pages) // 2):
        if i % 2 == 0:
            left.append(pages[2 * i])
            right.append(pages[2 * i + 1])
        else:
            left.append(pages[2 * i + 1])
            right.append(pages[2 * i])

    return right + left[::-1]


def merge_two_pages(page1: PageObject, page2: PageObject, vertical: bool) -> PageObject:
    """~~两个页面尺寸应该相同~~
    此处不要求页面尺寸相同，除了大小，还有纸张方向等都不统一。
    因此应该做一个判断。
    """
    page1 = copy.deepcopy(page1)
    page2 = copy.deepcopy(page2)

    width1 = page1.mediabox.width
    height1 = page1.mediabox.height
    width2 = page2.mediabox.width
    height2 = page2.mediabox.height
    ROTATION = 90  # 横向纸张应旋转90度（-90度是顺时针旋转，下面的变换也要修改）

    w1, h1 = sorted([width1, height1])
    w2, h2 = sorted([width2, height2])

    trans1 = Transformation()
    trans2 = Transformation()
    # 竖向页面合成横向页面
    if vertical:
        width = w1 + w2
        height = max(h1, h2)

        if width1 < height1:
            trans1 = trans1.translate(-page1.mediabox.left, -page1.mediabox.bottom)
        else:
            trans1 = trans1.rotate(ROTATION).translate(
                w1 - page1.mediabox.left, -page1.mediabox.bottom
            )
        if width2 < height2:
            trans2 = trans2.translate(w2 - page2.mediabox.left, -page2.mediabox.bottom)
        else:
            trans2 = trans2.rotate(ROTATION).translate(
                width - page2.mediabox.left, -page2.mediabox.bottom
            )
    else:
        width = max(w1, w2)
        height = h1 + h2

        if width1 > height1:
            trans1 = trans1.translate(-page1.mediabox.left, h2 - page1.mediabox.bottom)
        else:
            trans1 = trans1.rotate(ROTATION).translate(
                width - page1.mediabox.left, h2 - page1.mediabox.bottom
            )
        if width2 > height2:
            trans2 = trans2.translate(-page2.mediabox.left, -page2.mediabox.bottom)
        else:
            trans2 = trans2.rotate(ROTATION).translate(
                width - page2.mediabox.left, -page2.mediabox.bottom
            )

    res = PageObject.create_blank_page(None, width, height)
    res.merge_transformed_page(page1, trans1)
    res.merge_transformed_page(page2, trans2)
    return res


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
