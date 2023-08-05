# 预处理一下图片

import numpy as np
from PIL import ImageFont, ImageDraw, Image


def remove_water_mark(img: Image):
    if img.mode != "RGB":
        return None
    
    arr = np.array(img)
    i = arr[:, :] > (235, 235, 235)
    a = i.all((2, ))
    idx = np.nonzero(a)
    arr[idx] = (255, 255, 255)
    img_new = Image.fromarray(arr)
    return img_new


def remove_apparent(img: Image):
    image = Image.new('RGB', size=(img.width, img.height), color=(255, 255, 255))
    image.paste(img, (0, 0), mask=img)
    return image

def clean(img: Image):
    img = img.convert("L")
    img = img.crop((50, 50, img.width-50, img.height-50))
    arr = np.array(img)
    arr[(arr > 100).nonzero()] = 255
    return Image.fromarray(arr), arr

img = Image.open("./small.png")
img, arr = clean(img)
img.save("gray.png")

# 从左侧看这张图片
arr = 255 - arr
left = np.sum(arr, (1,), np.int64)
assert img.height == left.shape[0]

left_1 = left > 0
left_1 = left_1.astype(np.int8)
delta = np.diff(left_1)

start_indices = (delta == 1).nonzero()[0].tolist()
stop_indices = (delta == -1).nonzero()[0].tolist()

if stop_indices[0] < start_indices[0]:
    start_indices.insert(0, 0)

if start_indices[-1] > stop_indices[-1]:
    stop_indices.append(img.height-1)

assert len(start_indices) == len(stop_indices)

print(start_indices)
print(stop_indices)

sections = [(start, stop) for start, stop in zip(start_indices, stop_indices)]

print(sections)

for start, stop in sections:
    sect = arr[start: stop+1]
    up = np.sum(sect, (0,), np.int64)

    assert img.width == up.shape[0]

    up_1 = (up > 0).astype(np.int8)
    up_delta = np.diff(up_1)
    up_start_indices = (up_delta == 1).nonzero()[0].tolist()
    up_stop_indices = (up_delta == -1).nonzero()[0].tolist()

    if up_stop_indices[0] < up_start_indices[0]:
        up_start_indices.insert(0, 0)

    if up_start_indices[-1] > up_stop_indices[-1]:
        up_stop_indices.append(img.width-1)

    print(up_start_indices)
    print(up_stop_indices)
    break     
