from py_pdf.outline.parser import parse_from_text


def test_parse_from_text():
    s = """
        #目录#1
        ##目录#5
        ###目录#10
        #目录#11 """
    root = parse_from_text(s)

    assert root.children is not None
    assert len(root.children) == 2

    node = root.children[0]
    item = node.item
    assert item.level == 1
    assert item.title == "目录"
    assert item.page == 1

    assert node.children is not None
    assert len(node.children) == 1

    node = node.children[0]
    item = node.item
    assert item.level == 2
    assert item.title == "目录"
    assert item.page == 5

    assert node.children is not None
    assert len(node.children) == 1

    node = node.children[0]
    item = node.item
    assert item.level == 3
    assert item.title == "目录"
    assert item.page == 10

    node = root.children[1]
    item = node.item
    assert item.level == 1
    assert item.title == "目录"
    assert item.page == 11

    assert node.children is None
