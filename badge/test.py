# import library.radio


# from machine import Pin, SoftI2C
# import ssd1306
# # import framebuf
# import time

# MARGIN = 2
# PADDING = 3

# radio = library.radio.SI470X()
# i2c = SoftI2C(sda=Pin(5), scl=Pin(23))
# display = ssd1306.SSD1306_I2C(128, 64, i2c)
# timed_message = framebuf.FrameBuffer(bytearray(930), 124, 60,
#                                           framebuf.MONO_HLSB)

# width_space = 124 - PADDING * 2 - 4
# while True:
#     now = time.ticks_ms()
#     freq = radio.getFreq()
#     display.fill(0)
#     if now > 10000:
#         print('seeking')
#         radio.seekDown()
#         freq = radio.getFreq()
#         print(freq)
#     display.text(f'{now} {freq}', 0, 0, 1)
#     display.show()
#     time.sleep_ms(500)
#     if now > 5000:
#         timed_message.fill(0)
#         for i in range(PADDING):
#             timed_message.rect(i, i, 124 - i * 2, 60 - i * 2, 1)
#         timed_message.text('this is msg', PADDING + MARGIN, PADDING + MARGIN, 1)
#         display.blit(timed_message, MARGIN, MARGIN)
#         display.show()
#     elif now > 15000:
#         display.fill(0)
#         display.show()
#     time.sleep_ms(100)

# 10000: lonewolf, 5000: lonelycel
# INIT_PAIR (5000, 3) -> RESP_PAIR (10000, 4, 5000)
# 5000: /friend_request(token, uuid1, 10000) -> (uuid2, handle)
# 10000: /friend_request(token, uuid2, 5000) -> (uuid1, handle)

# /refresh_handles(token, uuid, list_of_uuids) -> list_of_new_handles
# {ir_id: uuid}

# [(f1, f2)]


class A:
    def __init__(self):
        self._b = 1
        self.c = 3

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, val):
        self._b = val


a = A()
print(a)
print(a.b)
a.b = 2
print(f"{a.b}")
print(globals())
