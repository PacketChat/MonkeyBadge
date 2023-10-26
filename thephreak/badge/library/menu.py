from machine import Pin, SoftI2C
import ssd1306
import uasyncio as asyncio
from library.button import ButtonHandler

class DisplayHandler:
    """
    A class for controlling an OLED display using the SSD1306 driver. The goal
    here is to display six lines of text, tried seven, but that fell off the
    bottom of the screen at that size.
    """

    def __init__(self, width, height, sda_pin, scl_pin):
        """
        Initialize the SSD1306 driver for controlling an OLED display.

        Args:
            width (int): Width of the display in pixels.
            height (int): Height of the display in pixels.
            sda_pin (int): Pin number for the SDA (data) line of the I2C bus.
            scl_pin (int): Pin number for the SCL (clock) line of the I2C bus.
        """
        self.i2c = SoftI2C(sda=Pin(sda_pin), scl=Pin(scl_pin))
        self.display = ssd1306.SSD1306_I2C(width, height, self.i2c)

    def clear(self):
        """
        Clear the display by filling it with black pixels.
        """
        self.display.fill(0)
        self.display.show()

    def print_text(self, lines):
        """
        Display text on the OLED screen.

        Args:
            list of strings, we only print the first 6 elements of the list.
        """
        self.clear()
        for i, line in enumerate(lines):
            self.display.text(line, 0, i * 11, 1)
        self.display.show()

class Menu:
    def __init__(self, name, items, parent=None):
        self.name = name
        self.items = items
        self.parent = parent
        self.selected_index = 0

    def next_item(self):
        self.selected_index += 1
        if self.selected_index >= len(self.items):
            self.selected_index = 0

    def prev_item(self):
        self.selected_index -= 1
        if self.selected_index < 0:
            self.selected_index = len(self.items) - 1

    def select(self):
        item = self.items[self.selected_index]
        if isinstance(item, Menu):
            return item
        else:
            # handle action or other types of menu items
            pass
        return self

    def back(self):
        return self.parent if self.parent else self

    def display(self, displayhandler):
        displayhandler.clear()
        result = []
        for i, item in enumerate(self.items):
            prefix = ">" if i == self.selected_index else " "
            result.append(f"{prefix}{item.name}")
        displayhandler.print_text(result)