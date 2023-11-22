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
    value = b.decode("utf-8").strip('\x00')
    del b
    return value

def eraseNVS(key):
    try:
        nvs.erase_key(key)
    except:
        # TODO: if we don't mask this users will likely see they can modify the value "API_SERVER"
        # pass
        print("Unable to erase key {}".format(key))

# Wifi Config
try:
    WIFI_SSID = getNVS("WIFI_SSID", 32)
except:
    pass

try:
    WIFI_PASSWORD = getNVS("WIFI_PASSWORD", 63)
except:
    pass

try:
    API_SERVER = getNVS("API_SERVER", 255)
except:
    pass

RESET_URL = "https://update.kafka.tel/firmware/reset.json"
UPDATE_URL = "https://update.kafka.tel/firmware/update.json"

# badge config
REG_KEY = "7bc78281-2036-41b2-8d98-fc23ec504e9a"
BUTTON_PINS = [4, 14, 15, 13]
BUTTON_PIN_DESCRIPTIONS = [
        "left up",
        "left down",
        "center",
        "right",
]

# OLED screen Config
OLED_HEIGHT = 64    # height (int): Height of the display in pixels.
OLED_WIDTH = 128    # width (int): Width of the display in pixels.
OLED_SDA_PIN = 5    # sda_pin (int): Pin number for the SDA (data) line of the I2C bus.
OLED_SCL_PIN = 23   #scl_pin (int): Pin number for the SCL (clock) line of the I2C bus.

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
Opcode = namedtuple('Opcode', ['code', 'additional_bytes'])
IR_OPCODES = {
        'DISCOVER': Opcode(1, 0),
        'HERE': Opcode(2, 0),
        'INIT_PAIR': Opcode(3, 0),
        'RESP_PAIR': Opcode(4, 2),
        'ACK_RESP': Opcode(5, 2),
        'EMOTE': Opcode(6, 3),
}
#REV_IR_OPCODES = {val.code: key for key, val in OPCODES.items()}

IR_TX_DELAY = 115  # delay between tx pulses in ms
# messages received after this much delay (in ms) become a new message
IR_RX_MAX_DELAY = 250
