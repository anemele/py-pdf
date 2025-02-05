from py_pdf.outline.parser import OutlineItem, OutlineItemNode, parse_from_text

test_cases = [
    (
        """
# 目录   1
## 目录  5
### 目录 10
# 目录   11""",
        [
            OutlineItemNode(
                OutlineItem(1, "目录", 1),
                [
                    OutlineItemNode(
                        OutlineItem(2, "目录", 5),
                        [OutlineItemNode(OutlineItem(3, "目录", 10), [])],
                    )
                ],
            ),
            OutlineItemNode(
                OutlineItem(1, "目录", 11),
                [],
            ),
        ],
    ),
    (
        """
# Chapter 1           1
## Section 1.1        2
### SubSection 1.1.1  3
### SubSection 1.1.2  4
### SubSection 1.1.3  5
## Section 1.2        6
# Chapter 2           7""",
        [
            OutlineItemNode(
                OutlineItem(1, "Chapter 1", 1),
                [
                    OutlineItemNode(
                        OutlineItem(2, "Section 1.1", 2),
                        [
                            OutlineItemNode(OutlineItem(3, "SubSection 1.1.1", 3), []),
                            OutlineItemNode(OutlineItem(3, "SubSection 1.1.2", 4), []),
                            OutlineItemNode(OutlineItem(3, "SubSection 1.1.3", 5), []),
                        ],
                    ),
                    OutlineItemNode(
                        OutlineItem(2, "Section 1.2", 6),
                        [],
                    ),
                ],
            ),
            OutlineItemNode(
                OutlineItem(1, "Chapter 2", 7),
                [],
            ),
        ],
    ),
]


def test_parse_from_text_parameterized():
    for s, expected in test_cases:
        assert parse_from_text(s).children == expected
