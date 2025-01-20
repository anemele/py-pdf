"""PDF大纲outline工具。

支持提取、设置、删除、重置大纲。"""

import re
from itertools import chain
from pathlib import Path
from typing import Optional

from pikepdf import Array, Name, OutlineItem, Page, Pdf, String

from py_pdf.utils import new_path_with_timestamp


def parse_outline_tree(
    outlines: OutlineItem | list[OutlineItem], level: int = 0, names=None
) -> list[tuple[int, int, str]]:
    if isinstance(outlines, (list, tuple)):
        return list(
            chain.from_iterable(
                parse_outline_tree(heading, level=level, names=names)
                for heading in outlines
            )
        )
    else:
        tmp = [(level, get_destiny_page_number(outlines, names) + 1, outlines.title)]
        return list(
            chain(
                tmp,
                chain.from_iterable(
                    (
                        parse_outline_tree(subheading, level=level + 1, names=names)
                        for subheading in outlines.children
                    ),
                ),
            )
        )


def get_destiny_page_number(outline: OutlineItem, names) -> int:
    def find_destiny(ref, names) -> int:
        resolved = None
        if isinstance(ref, Array):
            resolved = ref[0]
        else:
            for n in range(0, len(names) - 1, 2):
                if names[n] == ref:
                    if names[n + 1]._type_name == "array":
                        named_page = names[n + 1][0]
                    elif names[n + 1]._type_name == "dictionary":
                        named_page = names[n + 1].D[0]
                    else:
                        raise TypeError("Unknown type: %s" % type(names[n + 1]))
                    resolved = named_page
                    break

        if resolved is not None:
            # note: is this tpye hint error? .pyi says it is a method `()->int`, but a literal `int`
            return Page(resolved).index  # type: ignore
        return 0

    if outline.destination is None:
        return find_destiny(outline.action.D, names)  # type: ignore

    if isinstance(outline.destination, Array):
        # 12.3.2.2 Explicit destination
        # [raw_page, /PageLocation.SomeThing, integer parameters for viewport]
        raw_page = outline.destination[0]
        try:
            # note: is this tpye hint error? .pyi says it is a method `()->int`, but a literal `int`
            return Page(raw_page).index  # type: ignore
        except Exception:
            return find_destiny(outline.destination, names)
    elif isinstance(outline.destination, String):
        # 12.3.2.2 Named destination, byte string reference to Names
        # destiny = f'<Named Destination in document .Root.Names dictionary: {outline.destination}>'
        assert names is not None
        return find_destiny(outline.destination, names)
    elif isinstance(outline.destination, Name):
        # 12.3.2.2 Named destination, name object (PDF 1.1)
        # destiny = f'<Named Destination in document .Root.Dests dictionary: {outline.destination}>'
        return find_destiny(outline.destination, names)
    elif isinstance(outline.destination, int):
        # Page number
        return outline.destination

    return outline.destination


def get_outline(input_path: Path):
    # https://github.com/pikepdf/pikepdf/issues/149#issuecomment-860073511
    def has_nested_key(obj, keys):
        to_check = obj
        for key in keys:
            if key not in to_check.keys():
                return False
            to_check = to_check[key]
        return True

    def get_names(pdf: Pdf) -> list:
        # 此处可能出错（可能由于PDF被其它程序编辑过）
        if not hasattr(pdf, "Root"):
            return []
        if not has_nested_key(pdf.Root, ["/Names", "/Dests"]):
            return []
        obj = pdf.Root.Names.Dests
        ks = obj.keys()
        if "/Names" in ks:
            return obj.Names  # type: ignore
        elif "/Kids" in ks:
            return list(chain.from_iterable(map(get_names, obj.Kids)))  # type: ignore
        else:
            raise ValueError

    pdf = Pdf.open(input_path)
    names = get_names(pdf)

    with pdf.open_outline() as outline:
        outlines = parse_outline_tree(outline.root, names=names)
    if len(outlines) == 0:
        print(f"no outline is found in {input_path}")
        exit()

    max_length = max(len(title) + 2 * level for level, _, title in outlines) + 1

    def fmt(item):
        level, page, title = item
        level_space = "  " * level
        title_page_space = " " * (max_length - level * 2 - len(title))
        return f"{level_space}{title}{title_page_space}{page}"

    outline_txt_path = new_path_with_timestamp(input_path, ".txt")
    if outline_txt_path.exists():
        print(f"overwrite {outline_txt_path}")

    outline_txt_path.write_text("\n".join(map(fmt, outlines)), encoding="utf-8")

    print(f"save as\n{outline_txt_path}")


def _set_outline(pdf: Pdf, outline_txt_path: Path, page_offset: int):
    outline_lines = outline_txt_path.read_text(encoding="utf-8").strip().split("\n")

    MAX_PAGES = len(pdf.pages)

    outlines = list[OutlineItem]()
    history_indent = list[int]()

    # decide the level of each outline according to the relative indent size in each line
    #   no indent:          level 1
    #     small indent:     level 2
    #       larger indent:  level 3
    #   ...
    def get_parent_outline(
        current_indent: int, history_indent: list[int], outlines: list[OutlineItem]
    ) -> Optional[OutlineItem]:
        """The parent of A is the nearest outline whose indent is smaller than A's"""
        assert len(history_indent) == len(outlines)
        if current_indent == 0:
            return None
        for i in range(len(history_indent) - 1, -1, -1):
            # len(history_indent) - 1   ===>   0
            if history_indent[i] < current_indent:
                return outlines[i]
        return None

    with pdf.open_outline() as outline:
        for line in outline_lines:
            line2 = re.split(r"\s+", line.strip())
            if len(line2) == 1:
                continue

            indent_size = len(line) - len(line.lstrip())
            parent = get_parent_outline(indent_size, history_indent, outlines)
            history_indent.append(indent_size)

            title, page = " ".join(line2[:-1]), int(line2[-1]) - 1
            if page + page_offset >= MAX_PAGES:
                print(f"page index out of range: {page + page_offset} >= {MAX_PAGES}")
                exit()

            new_outline = OutlineItem(title, page + page_offset)
            if parent is None:
                outline.root.append(new_outline)
            else:
                parent.children.append(new_outline)
            outlines.append(new_outline)

    return pdf


def set_outline(input_path: Path, outline_txt_path: Path, page_offset: int):
    with Pdf.open(input_path) as pdf:
        new_pdf = _set_outline(pdf, outline_txt_path, page_offset)
        output_path = new_path_with_timestamp(input_path)
        new_pdf.save(output_path)


def remove_outline(input_path: Path):
    with Pdf.open(input_path) as pdf:
        pdf.open_outline().root.clear()
        output_path = new_path_with_timestamp(input_path)
        pdf.save(output_path)


def reset_outline(input_path: Path, outline_txt_path: Path, page_offset: int):
    with Pdf.open(input_path) as pdf:
        pdf.open_outline().root.clear()
        new_pdf = _set_outline(pdf, outline_txt_path, page_offset)
        output_path = new_path_with_timestamp(input_path)
        new_pdf.save(output_path)
