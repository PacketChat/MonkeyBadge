# color_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# As written, supports:
# Adafruit 1.5" 128*128 OLED display: https://www.adafruit.com/product/1431
# Adafruit 1.27" 128*96 display https://www.adafruit.com/product/1673
# Edit the driver import for other displays.

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# WIRING (Adafruit pin nos and names).
# Pyb   SSD
# 3v3   Vin (10)
# Gnd   Gnd (11)
# Y1    DC (3 DC)
# Y2    CS (5 OC OLEDCS)
# Y3    Rst (4 R RESET)
# Y6    CLK (2 CL SCK)
# Y8    DATA (1 SI MOSI)

import machine
import gc
from ssd1306 import SSD1306_I2C as SSD


class SSD(SSD1306_I2C):
    def __init__(self, i2c):
        super().__init__(128, 64, i2c)

# *** Choose your color display driver here ***
# Driver supporting non-STM platforms
# from drivers.ssd1351.ssd1351_generic import SSD1351 as SSD

# STM specific driver
# from drivers.ssd1351.ssd1351 import SSD1351 as SSD


gc.collect()  # Precaution before instantiating framebuf
