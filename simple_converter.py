import numpy as np
from PIL import ImageFont, ImageDraw, Image

class BlockType:
    def __init__(self) -> None:
        pass

class SimpleRecognizer:
    def __init__(self):
        pass

    def init_from_doc(self, doc):
        pass

    def recognize_block(self, block):
        
        return BlockType()

def clean(img: Image):
    img = img.convert("L")
    img = img.crop((50, 50, img.width-50, img.height-50))
    arr = np.array(img)
    arr[(arr > 100).nonzero()] = 255
    return Image.fromarray(arr), arr

class SubBlock:
    def __init__(self, parent, id_, border):
        self.parent = parent
        self.id_ = id_
        self.border = border
        self.start, self.stop = border

        self.prev = None
        self.next = None

class DocBlock:
    def __init__(self, doc, block_id, block_border) -> None:
        self.doc = doc
        self.block_id = block_id
        self.block_border = block_border

        self.start, self.stop = self.block_border
        self.arr = self.doc.arr[self.start: self.stop+1]

        self.prev = None
        self.next = None

        self.sub_blocks = None

    def build_inner(self):
        up = np.sum(self.arr, (0,), np.int64)

        assert self.doc.img.width == up.shape[0]

        up_1 = (up > 0).astype(np.int8)
        up_delta = np.diff(up_1)
        up_start_indices = (up_delta == 1).nonzero()[0].tolist()
        up_stop_indices = (up_delta == -1).nonzero()[0].tolist()

        if up_stop_indices[0] < up_start_indices[0]:
            up_start_indices.insert(0, 0)

        if up_start_indices[-1] > up_stop_indices[-1]:
            up_stop_indices.append(self.doc.img.width-1)

        self.sub_blocks = []

        sub_blocks_ = list(zip(up_start_indices, up_stop_indices))
        sub_blocks_len = len(sub_blocks_)
        for sub_block_id in range(sub_blocks_len):
            sub_block = SubBlock(self, sub_block_id, sub_blocks_[sub_block_id])
            self.sub_blocks.append(sub_block)

    def recognize(self):
        height = self.stop - self.start
        left = self.sub_blocks[0].start
        right = self.sub_blocks[-1].stop
        doc_padding_left = self.doc.get_padding_left()
        if height > 70 and left - doc_padding_left > 70:
            self.class_ = "img/table"
        else:
            self.class_ = "title/text/list"

    def build_markdwon_io(self, f):
        if self.doc_type is None:
            self.recognize()

        if self.doc_type.class_ == "title":
            level = self.doc_type.level_
            text = self.doc_type.text_
            out = "#" * level + " " + text + "\n"
            f.write(out)

class MarkdownImage:
    def __init__(self, path, debug=True):
        self.raw_path = path
        self.raw_img = Image.open(path)
        self.img, self.arr = clean(self.raw_img)
        self.width = self.img.width
        self.height = self.img.height

        if debug:
            self.img.save(path + ".gray.png")

        self.blocks = None
        self.build_tree()

    def build_tree(self):
        # 从左侧看这张图片
        arr = 255 - self.arr
        left = np.sum(arr, (1,), np.int64)
        assert self.height == left.shape[0]

        left_1 = left > 0
        left_1 = left_1.astype(np.int8)
        delta = np.diff(left_1)

        start_indices = (delta == 1).nonzero()[0].tolist()
        stop_indices = (delta == -1).nonzero()[0].tolist()

        if stop_indices[0] < start_indices[0]:
            start_indices.insert(0, 0)

        if start_indices[-1] > stop_indices[-1]:
            stop_indices.append(self.height)

        assert len(start_indices) == len(stop_indices)

        self.blocks = []
        block_ = [(start, stop) for start, stop in zip(start_indices, stop_indices)]
        block_len = len(block_)
        for block_id in range(block_len):
            start, stop = block_[block_id]
            block = DocBlock(self, block_id, (start, stop))
            block.build_inner()
            self.blocks.append(block)

    def build_markdown(self, out):
        with open(out, "w", encoding="utf-8") as f:
            return self.build_markdown_io(f)
        
    def build_markdown_io(self, f):
        for block in self.blocks:
            block.build_markdown_io(f)

if __name__ == "__main__":
    doc = MarkdownImage("./small_full.png", recognizer=SimpleRecognizer())
    doc.build_markdown("./test.md")



   
