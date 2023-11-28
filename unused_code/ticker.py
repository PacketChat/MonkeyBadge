"""oled ticker lib"""
from micropython import const
import framebuf

TIME_PER_CHAR = const(200)

class Ticker:
    def __init__(self, width=16, tpc=TIME_PER_CHAR, frame_skip=1):
        # width in characters
        self.width = width
        self.tpc = tpc
        # frame skip is a positive integer (anything over 8 is equivalent)
        self.frame_skip = max(1, min(frame_skip, 8))
        self._queue = []

    def ticker(self):
        fb = framebuf.FrameBuffer(bytearray(self.width * 8 + 8),
                                  self.width * 8 + 8,
                                  8,
                                  framebuf.MONO_HLSB)
        tb = ' ' * (self.width + 1)
        # this math isn't perfect for a frame skip that isn't a
        # multiple of 2 but it's close enough to not matter
        sleep_time = self.tpc // max(8 - self.frame_skip, 1)
        while True:
            try:
                tb = tb[1:] + self._queue.pop(0)
            except IndexError:
                # nothing in the queue
                if set(tb) == set(' '):
                    yield None, sleep_time
                    continue
                tb = tb[1:] + ' '
            for i in range(0, 8, self.frame_skip):
                fb.fill(0)
                fb.text(tb, 8 - i, 0, 1)
                yield fb, sleep_time

    def queue(self, msg):
        self._queue.extend(f'{msg}     ')
