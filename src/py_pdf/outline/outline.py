"""PDF大纲outline工具。

支持提取、设置、删除、重置大纲。"""

from itertools import chain, starmap
from pathlib import Path
from typing import Iterator

from pikepdf import Array, Name, OutlineItem, Page, Pdf, String

from .parser import OutlineItem as _OutlineItem
from .parser import OutlineItemNode, parse_from_file, serialize_lines


def parse_outline_tree(
    outlines: list[OutlineItem], level: int = 1, names=None
) -> list[_OutlineItem]:
    def cvt_outline_item(item: OutlineItem, level: int) -> _OutlineItem:
        return _OutlineItem(level, item.title, get_destiny_page_number(item, names))

    def dfs(node: OutlineItem, level: int) -> Iterator[tuple[OutlineItem, int]]:
        yield node, level
        for child in node.children:
            yield from dfs(child, level + 1)

    items = chain.from_iterable(dfs(outline, level) for outline in outlines)
    return list(starmap(cvt_outline_item, items))


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


def get_outline(input_path: Path, outline_txt_path: Path):
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
        return

    if outline_txt_path.exists():
        print(f"overwrite {outline_txt_path}")

    s = serialize_lines(outlines)
    outline_txt_path.write_text("\n".join(s), encoding="utf-8")

    print(f"save as\n{outline_txt_path}")


def set_outline(
    input_path: Path, output_path: Path, outline_txt_path: Path, page_offset: int
):
    MAX_PAGES: int

    def dfs(node: OutlineItemNode, parent: OutlineItem):
        item = node.item
        if item.page + page_offset >= MAX_PAGES:
            print(f"page index out of range: {item.page + page_offset} >= {MAX_PAGES}")
            raise
        new_outline = OutlineItem(item.title, item.page + page_offset)
        parent.children.append(new_outline)
        if node.children is None:
            return
        for child in node.children:
            dfs(child, new_outline)

    root = parse_from_file(str(outline_txt_path))
    outlineitem = OutlineItem("")
    try:
        dfs(root, outlineitem)
    except Exception:
        pass

    with Pdf.open(input_path) as pdf:
        MAX_PAGES = len(pdf.pages)

        with pdf.open_outline() as outline:
            outline.root[:] = outlineitem.children

        pdf.save(output_path)


def remove_outline(input_path: Path, output_path: Path):
    with Pdf.open(input_path) as pdf:
        # The next line does not work, I don't know why. 2025-01-20
        # pdf.open_outline().root.clear()
        with pdf.open_outline() as outline:
            outline.root.clear()

        pdf.save(output_path)
