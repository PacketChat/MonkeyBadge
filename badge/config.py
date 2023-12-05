"""configuration settings"""
from collections import namedtuple
from esp32 import NVS

nvs = NVS("monkeybadge")
WIFI_SSID = "HushCon"
WIFI_PASSWORD = "ThreeAmigos"
API_SERVER = "https://update.kafka.tel/api"


def setNVS(key, value):
    nvs.set_blob(key, value)
    nvs.commit()


def getNVS(key, size):
    b = bytearray(size)
    nvs.get_blob(key, b)
    value = b.decode("utf-8").strip("\x00")
    del b
    return value


def eraseNVS(key):
    try:
        nvs.erase_key(key)
    except Exception:
        # TODO: if we don't mask this users will likely see they can modify the value "API_SERVER"
        # pass
        print("Unable to erase key {}".format(key))


# Wifi Config
try:
    WIFI_SSID = getNVS("WIFI_SSID", 32)
except Exception:
    pass

try:
    WIFI_PASSWORD = getNVS("WIFI_PASSWORD", 63)
except Exception:
    pass

try:
    API_SERVER = getNVS("API_SERVER", 255)
except Exception:
    pass

RESET_URL = "https://update.kafka.tel/firmware/reset.json"
UPDATE_URL = "https://update.kafka.tel/firmware/update.json"

# badge config
REG_KEY = "7bc78281-2036-41b2-8d98-fc23ec504e9a"
MONKEY_PERIOD = 5000
CHECKIN_PERIOD = 60000
BUTTON_PINS = [4, 14, 15, 13]
BUTTON_PIN_DESCRIPTIONS = [
    "left up",
    "left down",
    "center",
    "right",
]

# OLED screen Config
OLED_HEIGHT = 64  # height (int): Height of the display in pixels.
OLED_WIDTH = 128  # width (int): Width of the display in pixels.
OLED_SDA_PIN = 5  # sda_pin (int): Pin number for the SDA (data) line of the I2C bus.
OLED_SCL_PIN = 23  # scl_pin (int): Pin number for the SCL (clock) line of the I2C bus.

# IR Pins (also double as right SAO GPIO pins)
IR_RX_PIN = 19  # SAO2 GPIO1
IR_TX_PIN = 17  # SAO2 GPIO2

# SAO1 Pins
SAO1_GPIO1 = 25
SAO1_GPIO2 = 27


# IR Definitions Follow
# examples (addr, data):
# DISCOVER: (0x000a, 0x01)
# HERE: (0x000b, 0x02)  <--- add to last seen
# INIT_PAIR: (0x000a, 0x03)
# RESP_PAIR: (0x000b, 0x04, 0x00, 0x0a) <--- responding to 0x000a
# ACK_RESP: (0x000a, 0x05, 0x00, 0x0b) <--- confirming 0x000b response
# EMOTE: (0x000a, 0x06, 0x01, 0x00, 0x0b) <--- a wants be to show emote 0x01 (lol)
# EMOTE: (0x000b, 0x06, 0x02, 0xff, 0xff) <--- b wants all badges in the vicinity
#                                              to show emote 0x02 (lmao)
# MONKEY: (0xffff, 0x07, 0xaa, 0xaa) <--- monkey ffff secret pass aaaa
# HIDDEN_OBJECT: (0xeeee, 0x08, 0xbb, 0xbb) <---- hidden object eeee with
#                                                 secret pass bbbb
Opcode = namedtuple("Opcode", ["code", "additional_bytes"])
IR_OPCODES = {
    "DISCOVER": Opcode(1, 0),
    "HERE": Opcode(2, 0),
    "INIT_PAIR": Opcode(3, 0),
    "RESP_PAIR": Opcode(4, 2),
    "ACK_RESP": Opcode(5, 2),
    "EMOTE": Opcode(6, 1),
    "MONKEY": Opcode(7, 2),
    "HIDDEN_OBJECT": Opcode(8, 2),
}
REV_IR_OPCODES = {val.code: key for key, val in IR_OPCODES.items()}

EMOTES = {
    (1 << 4) + 1: "lol",
    (1 << 4) + 2: "lmao",
    (1 << 4) + 3: "gtfo",
    (1 << 4) + 4: "rtfm",
    (1 << 4) + 5: "tldr",
    (1 << 4) + 6: "RNGesus",
    (1 << 4) + 7: "rofl",
    (1 << 4) + 8: "brb",
    (1 << 4) + 9: "stfu",
    (1 << 4) + 10: "wtf",
    (1 << 4) + 11: "ffs",
    (1 << 4) + 12: "smh",
    (1 << 4) + 13: "smdh",
    (1 << 4) + 14: "ifykyk",
    (1 << 4) + 15: "omg",
    (1 << 4) + 16: "uwu",
    (1 << 4) + 17: "skill issue",
    (1 << 4) + 18: "pspsps",
}


IR_TX_DELAY = 175  # delay between tx pulses in ms
# messages received after this much delay (in ms) become a new message
IR_RX_MAX_DELAY = 250

CLEAN_BADGE_AFTER = 120000  # 120s

# Battery monitor:
FULLY_CHARGED_ADC_VALUE = 2404
DEPLETED_ADC_VALUE = 1500
MAX_VOLTAGE = 2.4
ADC_PIN = 36

LOCKED_FREQ = 107.5
