"""Image to framebuffer utilities"""
from typing import BinaryIO, Tuple, Generator

import PIL.Image
import numpy as np

PYTHON_MSG = '''
{name}_arr = {bytearray!r}
{name} = framebuf.FrameBuffer({name}_arr, {width}, {height}, framebuf.MONO_HLSB)
'''


def _arr2ba(arr: np.array) -> bytearray:
    ret_bytes = bytearray()
    for row in arr:
        for i in range(0, len(row), 8):
            narr = row[i: i + 8]
            byte = 0
            for idx, j in enumerate(narr):
                byte = byte + (j << (7 - idx))
            ret_bytes.append(byte)
    return ret_bytes


def bmp2bytearray(
        filename: str | bytes,
        background_color: int = 1) -> Tuple[bytearray, Tuple[int, int]]:
    """given a monochrome bmp image returns a bytearray and dimensions
        that are usable in a MONO_HLSB framebuffer
    """
    img = PIL.Image.open(filename)
    arr = np.array(img, dtype=np.uint8)
    height, width = arr.shape

    # normalize array so a) all elements are either 1 or 0 and also prob flip
    # black (0) to white(1) since OLED draws white on black, not black on white
    norm = np.vectorize(lambda e: 0 if e == background_color else 1)(arr)

    ret_bytes = _arr2ba(norm)
    return ret_bytes, (width, height)


def bmp2python(name: str,
               filename: str | bytes,
               background_color: int = 1):
    """Prints some python code to create a framebuffer from an image"""
    byte_array, (width, height) = bmp2bytearray(filename, background_color)

    print(PYTHON_MSG.format(name=name,
                            bytearray=byte_array,
                            width=width,
                            height=height))


def bmp2sprite(filename: str | bytes,
               frame_width: int,
               frame_height: int,
               background_color: int = 1) -> Generator[None, bytearray, None]:
    """Yields all frames in a sprite sheet
        order is top left to bottom right, scanning from left to right then
        up to down
    """
    img = PIL.Image.open(filename)
    arr = np.array(img, dtype=np.uint8)
    height, width = arr.shape
    assert height and height % frame_height == 0
    assert width and width % frame_width == 0
    norm = np.vectorize(lambda e: 0 if e == background_color else 1)(arr)

    # slice frame rows
    for i in range(0, height, frame_height):
        # slice row by frame column
        for j in range(0, width, frame_width):
            frame = norm[i:i + frame_height, j:j + frame_width]
            yield _arr2ba(frame)


# class BadgeSprite:
#     """a class to display a multi-frame image on the OLED badge

#         Usage: pass a spritesheet created with `bmp2sprite`
#     """
#     def __init__
