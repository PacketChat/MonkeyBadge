import machine
from machine import Pin, SoftI2C
import time
import ssd1306

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

    def show_text(self, line1='', line2='', line3='', line4='', line5='', line6=''):
        """
        Display text on the OLED screen.

        Args:
            line1 (str): Text for line 1.
            line2 (str): Text for line 2.
            line3 (str): Text for line 3.
            line4 (str): Text for line 4.
            line5 (str): Text for line 5.
            line6 (str): Text for line 6.
        """
        self.clear()
        self.display.text(line1, 0, 0, 1)
        self.display.text(line2, 0, 11, 1)
        self.display.text(line3, 0, 22, 1)
        self.display.text(line4, 0, 33, 1)
        self.display.text(line5, 0, 44, 1)
        self.display.text(line6, 0, 55, 1)
        self.display.show()

class MenuHandler:
    """
    A class for creating and managing a menu system using an OLED display and
    buttons.
    """

    def __init__(self, options, oled, button_pins, button_functions):
        """
        Initialize the menu.

        Args:
            options (list): List of menu options.
            oled (SSD1306): An instance of the SSD1306 class for displaying
            the menu.
            button_pins (list): List of button pin numbers.
            button_functions (list): List of callback functions for buttons.
        """
        self.options = options
        self.oled = oled
        self.selected_option = 0
        self.buttons = [Button(pin, callback) for pin, callback in zip(button_pins, button_functions)]

    def prev_option(self, button=None):
        """
        Move to the previous menu option.

        Args:
            button: Button instance (not used).
        """
        self.selected_option = (self.selected_option - 1) % len(self.options)
        self.display_menu()

    def next_option(self, button=None):
        """
        Move to the next menu option.

        Args:
            button: Button instance (not used).
        """
        self.selected_option = (self.selected_option + 1) % len(self.options)
        self.display_menu()

    def execute_option(self, button=None):
        """
        Execute the selected menu option.

        Args:
            button: Button instance (not used).
        """
        self.oled.clear()
        self.oled.show_text("Executing:", self.options[self.selected_option])
        time.sleep(2)
        self.oled.clear()
        self.display_menu()

    def back_to_main(self, button=None):
        """
        Return to the main menu.

        Args:
            button: Button instance (not used).
        """
        self.selected_option = 0
        self.display_menu()

    def display_menu(self):
        """
        Display the menu options on the OLED screen.
        """
        lines = []
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                lines.append("* " + option)
            else:
                lines.append(option)
        while len(lines) < 6:
            lines.append('')
        self.oled.show_text(*lines)

    def run(self):
        """
        Start running the menu loop, handling button presses and updating the
        display.
        """
        while True:
            for button in self.buttons:
                if not button.debounce():
                    if button.callback is not None:
                        button.callback()

            time.sleep(0.2)