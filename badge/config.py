"""configuration settings"""
from collections import namedtuple

# Wifi Config
# WIFI_SSID = "WillHouse6"
# WIFI_PASSWORD = "williams123"
WIFI_SSID = 'beerus'
WIFI_PASSWORD = 'get 0ff my l4wn'

# badge config
REG_KEY = "7bc78281-2036-41b2-8d98-fc23ec504e9a"
API_SERVER = "http://192.168.184.183:8000"
# CHECKIN_PERIOD = 60
CHECKIN_PERIOD = 5
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
# MONKEY: (0xffff, 0x07, 0xaa, 0xaa) <--- monkey ffff secret pass aaaa
# HIDDEN_OBJECT: (0xeeee, 0x08, 0xbb, 0xbb) <---- hidden object eeee with
#                                                 secret pass bbbb
Opcode = namedtuple('Opcode', ['code', 'additional_bytes'])
IR_OPCODES = {
        'DISCOVER': Opcode(1, 0),
        'HERE': Opcode(2, 0),
        'INIT_PAIR': Opcode(3, 0),
        'RESP_PAIR': Opcode(4, 2),
        'ACK_RESP': Opcode(5, 2),
        'EMOTE': Opcode(6, 3),
        'MONKEY': Opcode(7, 2),
        'HIDDEN_OBJECT': Opcode(8, 2)
}
REV_IR_OPCODES = {val.code: key for key, val in IR_OPCODES.items()}

IR_TX_DELAY = 115  # delay between tx pulses in ms
# messages received after this much delay (in ms) become a new message
IR_RX_MAX_DELAY = 250
