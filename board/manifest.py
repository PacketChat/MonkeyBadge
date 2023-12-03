# Include modules specified by the MicroPython port
freeze("$(PORT_DIR)/modules")
include("$(MPY_DIR)/extmod/asyncio")

# Useful networking-related packages.
require("bundle-networking")

# Require some micropython-lib modules.
require("logging")
require("neopixel")
require("ssd1306")
require("umqtt.robust")
require("umqtt.simple")
require("upysh")

# Retrieve badge code from the repository
freeze("$(BOARD_DIR)/../badge")
