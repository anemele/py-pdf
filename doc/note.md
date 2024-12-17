# PDF File Structure and Operations

## crop is not real crop

PDF 的裁剪功能是「假裁剪」，它更像是「折叠」而不是「裁剪」。
参考[这篇文章](https://sspai.com/post/61716)。
另外，[pypdf文档](https://pypdf.readthedocs.io/en/stable/user/cropping-and-transforming.html#cropping-and-transforming-pdfs)
也指出，裁剪功能只是让框外元素不可见，并不会真正删除它们。

```markdown
**Note**
Just because content is no longer visible, it is not gone. Cropping works by adjusting the viewbox. That means content that was cropped away can still be restored.
```
