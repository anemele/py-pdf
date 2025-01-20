"""大纲解析器

约定：
大纲文件是一个 markdown 文件，每行表示一个目录项，格式为：

```
#目录#1
##目录#5
###目录#10
#目录#11
...
```

解释：
- 行首的 `#` 表示目录级别，每多一个 `#` 表示目录级别更深；
- 行尾的 `#` 后面的数字表示页码；
- 中间的所有内容表示目录名称，可以包含空格，但首尾空格会被忽略。
"""

import re
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Iterator, Optional


@dataclass
class OutlineItem:
    level: int
    title: str
    page: int


def parse_line(line: str) -> Optional[OutlineItem]:
    line = line.strip()
    res = re.match(r"^(#+)([\s\S]+?)#(\d+)$", line)
    if res is None:
        return None
    level = len(res.group(1))
    title = res.group(2).strip()
    page = int(res.group(3))
    return OutlineItem(level, title, page)


def serialize_item(item: OutlineItem) -> str:
    return f"{'#' * item.level}{item.title}#{item.page}"


def parse_lines(lines: Iterable[str]) -> Iterable[OutlineItem]:
    for line in lines:
        item = parse_line(line)
        if item is None:
            print(f"Warning: invalid outline item: {line}")
            continue
        yield item


def serialize_lines(items: Iterable[OutlineItem]) -> Iterable[str]:
    yield from map(serialize_item, items)


@dataclass
class OutlineItemNode:
    item: OutlineItem
    children: Optional[list["OutlineItemNode"]] = None


def build_outline_tree(items: Iterable[OutlineItem]) -> OutlineItemNode:
    root = OutlineItemNode(OutlineItem(0, "", 0))
    stack = [root]
    for item in items:
        while item.level <= stack[-1].item.level:
            stack.pop()
        parent = stack[-1]
        if parent.children is None:
            parent.children = []
        node = OutlineItemNode(item)
        parent.children.append(node)
        stack.append(node)
    return root


def serialize_outline_tree(root: OutlineItemNode) -> Iterable[str]:
    def dfs(node: OutlineItemNode) -> Iterator[OutlineItem]:
        yield node.item
        if node.children is not None:
            maps = map(dfs, node.children)
            yield from chain.from_iterable(maps)

    items = dfs(root)
    next(items)  # skip root item
    yield from map(serialize_item, items)


def parse_from_text(s: str) -> OutlineItemNode:
    lines = s.split("\n")
    items = parse_lines(lines)
    return build_outline_tree(items)


def serialize_to_text(root: OutlineItemNode) -> str:
    lines = serialize_outline_tree(root)
    return "\n".join(lines) + "\n"


def parse_from_file(filename: str) -> OutlineItemNode:
    with open(filename, "r", encoding="utf-8") as f:
        s = f.read()
    return parse_from_text(s)


def serialize_to_file(root: OutlineItemNode, filename: str) -> None:
    s = serialize_to_text(root)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(s)
