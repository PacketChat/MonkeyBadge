"""configuration settings"""

# Wifi Config
WIFI_SSID = "WillHouse6"
WIFI_PASSWORD = "williams123"

# badge config
REG_KEY = "7bc78281-2036-41b2-8d98-fc23ec504e9a"
API_SERVER = "http://192.168.2.165:8000"
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
