import esp32
import time
import math
import random
import framebuf
from machine import Pin, I2C
from micropython import const
from uctypes import struct, addressof
from uctypes import BF_POS, BF_LEN, UINT16, UINT32, BFUINT16, BFUINT32, BIG_ENDIAN
import oled
import neopixel
import si470x
import static

# Color constants & intensity function stolen from the MIT licensed
# CircuitPython library `adafruit_led_animation.color` by Kattni Rembor
#
# helper LED functions pulled from Stack Overflow
#
# | Pin Name |  Purpose   |
# | -------- | ---------- |
# |  IO1     |  UART0_TX   |
# |  IO3     |  UART0_RX   |
# |  IO4     |  BTN_UP    |
# |  IO5     |  I2C1_SDA  |
# |  IO12    |  MIC       |
# |  IO13    |  BTN_MUTE  |
# |  IO14    |  BTN_DOWN  |
# |  IO15    |  BTN_ENTER |
# |  IO16    |  FM_RST    |
# |  IO17    |  IR_TX / SAO2_GP2  |
# |  IO18    |  NEOPX     |
# |  IO19    |  SAO2_GP1  |
# |  IO21    |  I2C0_SDA  |
# |  IO22    |  I2C0_SCL  |
# |  IO23    |  I2C1_SCL  |
# |  IO25    |  IR_RX / SAO1_GP1  |
# |  IO26    |  INFRARCV  |
# |  IO27    |  SAO1_GP2  |
# |  IO34    |  ROUT      |
# |  IO35    |  LOUT      |

# https://github.com/adafruit/Adafruit_CircuitPython_LED_Animation/blob/2e97f14805e3a32e7dab25980da70843cf589630/adafruit_led_animation/color.py

logo = bytearray(
    b"\x00\x00\xff\x00\x00\x00\x0e\x00p\x00\x000\x00\x0c\x00\x00@\x00\x02\x00\x01\x80<\x01\x80\x03\x03\xff\xc0\xc0\x04\x0f\xff\xf0 \x0c\x1f\xff\xf80\x08\x7f\xfef\x10\x10\xff\xfeg\x08 \xff\xfeg\x04!\xff\xfeg\x84C\xff\xfeg\xc2C\xff\xfe\x07\xc2G\xff\xfe\x07\xe2\x87\xff\xfe\x07\xe1\x87\xe0~g\xe1\x87\x80\x1eg\xe1\x8f\x00\x0eg\xf1\x8e\x0f\x06g\xf1\x8f\x10\x82e\xf1\x8f\xe0\xc1\xf8q\x87\xe6``a\x87\xe6p\x00\xe1\x87\xe6|\x03\xe1G\xe6\x7f\x0f\xe2C\xe7\xff\xff\xc2C\xe7\xff\xff\xc2!\xe6\x7f\xff\x84 \xe6\x7f\xff\x04\x10\xe6\x7f\xff\x08\x08`\xff\xfe\x10\x0c\x10\xff\xf80\x04\x0f\xff\xf0 \x03\x03\xff\xc0\xc0\x01\x80<\x01\x80\x00@\x00\x02\x00\x000\x00\x0c\x00\x00\x0e\x00p\x00\x00\x01\xff\x80\x00"
)

RED = (255, 0, 0)
"""Red."""
YELLOW = (255, 150, 0)
"""Yellow."""
ORANGE = (255, 40, 0)
"""Orange."""
GREEN = (0, 255, 0)
"""Green."""
TEAL = (0, 255, 120)
"""Teal."""
CYAN = (0, 255, 255)
"""Cyan."""
BLUE = (0, 0, 255)
"""Blue."""
PURPLE = (180, 0, 255)
"""Purple."""
MAGENTA = (255, 0, 20)
"""Magenta."""
WHITE = (255, 255, 255)
"""White."""
BLACK = (0, 0, 0)
"""Black or off."""

GOLD = (255, 222, 30)
"""Gold."""
PINK = (242, 90, 255)
"""Pink."""
AQUA = (50, 255, 255)
"""Aqua."""
JADE = (0, 255, 40)
"""Jade."""
AMBER = (255, 100, 0)
"""Amber."""
OLD_LACE = (253, 245, 230)  # Warm white.
"""Old lace or warm white."""

RGBW_WHITE_RGB = (255, 255, 255, 0)
"""RGBW_WHITE_RGB is for RGBW strips to illuminate only the RGB diodes."""
RGBW_WHITE_W = (0, 0, 0, 255)
"""RGBW_WHITE_W is for RGBW strips to illuminate only White diode."""
RGBW_WHITE_RGBW = (255, 255, 255, 255)
"""RGBW_WHITE_RGBW is for RGBW strips to illuminate the RGB and White diodes."""

RAINBOW = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)
"""RAINBOW is a list of colors to use for cycling through.
Includes, in order: red, orange, yellow, green, blue, and purple."""


def calculate_intensity(color, intensity=1.0):
    """
    Takes a RGB[W] color tuple and adjusts the intensity.
    :param float intensity:
    :param color: color value (tuple, list or int)
    :return: color
    """
    # Note: This code intentionally avoids list comprehensions and intermediate variables
    # for an approximately 2x performance gain.
    if isinstance(color, int):
        return (
            (int((color & 0xFF0000) * intensity) & 0xFF0000)
            | (int((color & 0xFF00) * intensity) & 0xFF00)
            | (int((color & 0xFF) * intensity) & 0xFF)
        )

    if len(color) == 3:
        return (
            int(color[0] * intensity),
            int(color[1] * intensity),
            int(color[2] * intensity),
        )
    if len(color) == 4 and isinstance(color[3], float):
        return (
            int(color[0] * intensity),
            int(color[1] * intensity),
            int(color[2] * intensity),
            color[3],
        )
    return (
        int(color[0] * intensity),
        int(color[1] * intensity),
        int(color[2] * intensity),
        int(color[3] * intensity),
    )


def rgb_to_hsv(rgb_color):
    """Converts colors from the RGB color space to the HSV color space.
    Parameters
    ----------
    rgb_color : tuple (r, g, b)
        Color in the RGB color space
    Returns
    -------
    tuple (h, s, v)
        Color in the HSV color space
    """
    (r, g, b) = rgb_color
    r = float(1 / 255 * r)
    g = float(1 / 255 * g)
    b = float(1 / 255 * b)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, v = high, high, high

    d = high - low
    s = 0 if high == 0 else d / high

    if high == low:
        h = 0.0
    else:
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return h, s, v


def hsv_to_rgb(hsv_color):
    """Converts colors from the HSV color space to the RGB color space.
    Parameters
    ----------
    hsv_color : tuple (h, s, v)
        Color in the HSV color space
    Returns
    -------
    tuple (r, g, b)
        Color in the RGB color space
    """
    (h, s, v) = hsv_color
    i = math.floor(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)

    r, g, b = [
        (v, t, p),
        (q, v, p),
        (p, v, t),
        (p, q, v),
        (t, p, v),
        (v, p, q),
    ][int(i % 6)]
    r = int(255 * r)
    g = int(255 * g)
    b = int(255 * b)
    return r, g, b


def hex_to_rgb(self, hex):
    """Returns the RGB value of a Hex Colour
    Parameters
    ----------
    hex : string
        The hex representation of a RGB color
        Example:
            hex_to_rgb("123456")
    """
    return tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))


class LedSet(object):
    def __init__(self, start, end, color=RED):
        pass


CONFIG_FIELDS = {
    "ID": 0 << BF_POS | 16 << BF_LEN | BFUINT32,
    "VOL": 16 << BF_POS | 4 << BF_LEN | BFUINT32,
    "FREQ": 20 << BF_POS | 10 << BF_LEN | BFUINT32,
}

WIFI_FIELDS = {
    "SSID": 32 << BF_POS | 32 << BF_LEN | BFUINT32,
    "KEY": 64 << BF_POS | 32 << BF_LEN | BFUINT32,
}

NVS = {
    "CONFIG": (0x00, CONFIG_FIELDS),
    "WIFI": (0x02, WIFI_FIELDS),
}


class Config(object):
    def __init__(self, ns="BADGE"):
        self.nvs = esp32.NVS(ns)
        self.buffer = bytearray(128)
        self.fields = struct(addressof(self.buffer), NVS, BIG_ENDIAN)
        try:
            self.nvs.get_blob("config", self.buffer)
        except OSError:
            # Reset flash if there are no contents in non-volatile storage
            self._initFlash()

    def _initFlash(self):
        """Basic routine to initialize the contents of the flash and generate
        a unique ID for the board.
        """

        self.fields.CONFIG.ID = int(random.random() * (2**16))
        self.commitConfig()

    def getConfig(self):
        self.nvs.get_blob("config", self.buffer)
        return {
            "ID": self.fields.CONFIG.ID,
            "VOL": self.fields.CONFIG.VOL,
            "FREQ": self.fields.CONFIG.FREQ,
            "SSID": self.fields.WIFI.SSID,
            "KEY": self.fields.WIFI.KEY,
        }

    def commitConfig(self):
        self.nvs.set_blob("config", self.buffer)
        return self.nvs.commit()

    def _wipeConfig(self):
        self.nvs.set_blob("config", 0x0)
        return self.nvs.commit()


config = Config()


class Badge(object):
    def __init__(
        self,
        UART0_TX=1,
        UART0_RX=3,
        BTN_UP=4,
        I2C1_SDA=5,
        MIC=12,
        BTN_MUTE=13,
        BTN_DOWN=14,
        BTN_ENTER=15,
        FM_RST=16,
        IR_TX=17,
        NEOPX=18,
        SAO2_GP1=19,
        I2C0_SDA=21,
        I2C0_SCL=22,
        I2C1_SCL=23,
        IR_RX=25,
        SAO1_GP2=27,
        ROUT=34,
        LOUT=35,
        NEOPX_COUNT=10,
    ):
        self.UART0_TX = UART0_TX
        self.UART0_RX = UART0_RX
        self.BTN_UP = Pin(BTN_UP, Pin.IN, Pin.PULL_UP)
        self.I2C1_SDA = I2C1_SDA
        self.MIC = MIC
        self.BTN_MUTE = Pin(BTN_MUTE, Pin.IN, Pin.PULL_UP)
        self.BTN_DOWN = Pin(BTN_DOWN, Pin.IN, Pin.PULL_UP)
        self.BTN_ENTER = Pin(BTN_ENTER, Pin.IN, Pin.PULL_UP)
        self.FM_RST = Pin(FM_RST, Pin.OUT, Pin.PULL_UP)
        self.IR_TX = Pin(IR_TX, Pin.OUT)
        self.NEOPX = neopixel.NeoPixel(Pin(NEOPX), NEOPX_COUNT)
        self.SAO2_GP1 = SAO2_GP1
        self.I2C0_SDA = I2C0_SDA
        self.I2C0_SCL = I2C0_SCL
        self.I2C1_SCL = I2C1_SCL
        self.IR_RX = IR_RX
        self.SAO1_GP2 = Pin(SAO1_GP2, Pin.OUT)
        self.ROUT = ROUT
        self.LOUT = LOUT
        self.I2C1 = I2C(1, scl=Pin(I2C1_SCL), sda=Pin(I2C1_SDA))
        try:
            self.DISPLAY = oled.OLED(self.I2C1)
        except OSError:
            print("ERROR: Unable to enumerate OLED display on I2C bus: ", self.I2C1)
        self.FM = si470x.SI470X()
        self.baudrate = 115200

    def getID(self):
        try:
            self.ID = config.getConfig()["ID"]
        except:
            config._initFlash()
            self.ID = config.getConfig()["ID"]
        return self.ID

    def welcomeDisplay(self):
        d = self.DISPLAY
        d.poweron()
        d.fill(0)
        name = idToName(self.getID())
        fbuf = framebuf.FrameBuffer(logo, 40, 40, framebuf.MONO_HLSB)
        d.blit(fbuf, 0, 0)
        d.text("Welcome to", 40, 6, 1)
        d.text("Hushcon XX", 40, 18, 1)
        d.text(f"{name}", 0, 36, 1)
        d.show()

    def setColor(self, color=BLUE, bright=1.0):
        if type(color) is str:
            color = hex_to_rgb(self, color)
        if bright < 1.0:
            h, s, _ = rgb_to_hsv(color)
            v = bright
            color = hsv_to_rgb((h, s, v))
        else:
            bright = math.ceil(bright * 31)
            (r, g, b) = color
            color = (r, g, b, bright)
        self.NEOPX.fill(color)
        self.NEOPX.write()

    def setBaudRate(self, rate):
        self.baudrate = rate

    def startUART(self):
        from machine import UART

        uart = UART(0, baudrate=self.baudrate, tx=self.UART0_TX, rx=self.UART0_RX)
        return uart

    def resetFM(self):
        self.FM_RST.on()
        time.sleep(0.500)
        self.FM_RST.off()
        time.sleep(0.001)
        self.FM_RST.on()
        time.sleep(0.005)


def idToName(i):
    low = i // 256
    hi = i % 256
    badgeName = "{} {}".format(static.colors[hi]["cname"], static.animals[low])
    return badgeName
