from machine import Pin, SoftI2C
import framebuf
import ssd1306

# 'HCcircle', 60x60px

# deactivate black temporarily
# fmt: off
HC_LOGO = [
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f,
    0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0xff, 0xfe, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x1f, 0xff, 0xff, 0x80, 0x00, 0x00, 0x00, 0x00, 0x7f, 0xff,
    0xff, 0xe0, 0x00, 0x00, 0x00, 0x01, 0xff, 0xff, 0xff, 0xf8, 0x00, 0x00,
    0x00, 0x07, 0xff, 0xff, 0xff, 0xfe, 0x00, 0x00, 0x00, 0x0f, 0xff, 0x00,
    0x0f, 0xff, 0x00, 0x00, 0x00, 0x1f, 0xf8, 0x00, 0x01, 0xff, 0x80, 0x00,
    0x00, 0x3f, 0xe0, 0x00, 0x00, 0x7f, 0xc0, 0x00, 0x00, 0x7f, 0x80, 0x00,
    0x00, 0x1f, 0xe0, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00, 0x0f, 0xf0, 0x00,
    0x01, 0xfe, 0x00, 0x00, 0x1e, 0xe7, 0xf8, 0x00, 0x03, 0xfc, 0x00, 0x00,
    0x1e, 0xe3, 0xfc, 0x00, 0x03, 0xf8, 0x00, 0x00, 0x1e, 0xe1, 0xfc, 0x00,
    0x07, 0xf0, 0x00, 0x00, 0x1e, 0xe0, 0xfe, 0x00, 0x07, 0xe0, 0x00, 0x00,
    0x1e, 0xe0, 0x7e, 0x00, 0x0f, 0xc0, 0x00, 0x00, 0x1e, 0xe0, 0x3f, 0x00,
    0x0f, 0xc0, 0x00, 0x00, 0x1e, 0xe0, 0x3f, 0x00, 0x1f, 0x80, 0x00, 0x00,
    0x1f, 0xe0, 0x1f, 0x80, 0x1f, 0x80, 0x00, 0x00, 0x1f, 0xe0, 0x1f, 0x80,
    0x3f, 0x00, 0x00, 0x00, 0x1f, 0xe0, 0x0f, 0xc0, 0x3f, 0x00, 0x00, 0x00,
    0x1f, 0xe0, 0x0f, 0xc0, 0x3f, 0x00, 0x00, 0x00, 0x1e, 0xe0, 0x0f, 0xc0,
    0x3e, 0x00, 0xff, 0x80, 0x1e, 0xe0, 0x07, 0xc0, 0x3e, 0x01, 0xff, 0xe0,
    0x1e, 0xe0, 0x07, 0xc0, 0x7e, 0x07, 0xff, 0xf8, 0x1e, 0xe0, 0x07, 0xe0,
    0x7e, 0x0f, 0xff, 0xfc, 0x1e, 0xe0, 0x07, 0xe0, 0x7e, 0x1f, 0xff, 0xfe,
    0x1e, 0xe0, 0x07, 0xe0, 0x7e, 0x3f, 0xc0, 0xff, 0x1e, 0xe0, 0x07, 0xe0,
    0x7e, 0x1f, 0x1e, 0x3f, 0x9e, 0xe6, 0x07, 0xe0, 0x7e, 0x06, 0x3f, 0x1f,
    0xc0, 0x0f, 0x07, 0xe0, 0x7e, 0x00, 0x3f, 0x0f, 0xe0, 0x1f, 0xc7, 0xe0,
    0x7e, 0x00, 0x77, 0x07, 0xf8, 0x7f, 0x87, 0xe0, 0x3e, 0x00, 0x77, 0x83,
    0xff, 0xff, 0x07, 0xc0, 0x3e, 0x00, 0x77, 0x81, 0xff, 0xfe, 0x07, 0xc0,
    0x3f, 0x00, 0x77, 0x80, 0xff, 0xfc, 0x0f, 0xc0, 0x3f, 0x00, 0x77, 0x80,
    0x3f, 0xf8, 0x0f, 0xc0, 0x3f, 0x00, 0x77, 0x80, 0x0f, 0xc0, 0x0f, 0xc0,
    0x1f, 0x80, 0x70, 0x00, 0x00, 0x00, 0x1f, 0x80, 0x1f, 0x80, 0x70, 0x00,
    0x00, 0x00, 0x1f, 0x80, 0x0f, 0xc0, 0x70, 0x00, 0x00, 0x00, 0x3f, 0x00,
    0x0f, 0xc0, 0x77, 0x80, 0x00, 0x00, 0x3f, 0x00, 0x07, 0xe0, 0x77, 0x80,
    0x00, 0x00, 0x7e, 0x00, 0x07, 0xf0, 0x77, 0x80, 0x00, 0x00, 0xfe, 0x00,
    0x03, 0xf8, 0x77, 0x80, 0x00, 0x01, 0xfc, 0x00, 0x03, 0xf8, 0x7f, 0x00,
    0x00, 0x01, 0xfc, 0x00, 0x01, 0xfe, 0x7f, 0x00, 0x00, 0x07, 0xf8, 0x00,
    0x00, 0xff, 0x3f, 0x00, 0x00, 0x0f, 0xf0, 0x00, 0x00, 0x7f, 0x9c, 0x00,
    0x00, 0x1f, 0xe0, 0x00, 0x00, 0x3f, 0xe0, 0x00, 0x00, 0x7f, 0xc0, 0x00,
    0x00, 0x1f, 0xf8, 0x00, 0x01, 0xff, 0x80, 0x00, 0x00, 0x0f, 0xff, 0x00,
    0x0f, 0xff, 0x00, 0x00, 0x00, 0x07, 0xff, 0xff, 0xff, 0xfe, 0x00, 0x00,
    0x00, 0x01, 0xff, 0xff, 0xff, 0xf8, 0x00, 0x00, 0x00, 0x00, 0x7f, 0xff,
    0xff, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x1f, 0xff, 0xff, 0x80, 0x00, 0x00,
    0x00, 0x00, 0x07, 0xff, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f,
    0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]
# fmt: on


class DisplayHandler:
    """
    A class for controlling an OLED display using the SSD1306 driver.
    The screen will be split up into three sections of 1-7
    (header-body) where the header will display contextual information,
    the body will display menu items or context information
    """

    MARGIN = 2
    PADDING = 2

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

        self.header_right = framebuf.FrameBuffer(
            bytearray(48), 48, 8, framebuf.MONO_HLSB
        )
        self.header_left = framebuf.FrameBuffer(
            bytearray(80), 80, 8, framebuf.MONO_HLSB
        )
        self.body = framebuf.FrameBuffer(
            bytearray(128 * 7), 128, 8 * 7, framebuf.MONO_HLSB
        )

        self.timed_message = framebuf.FrameBuffer(
            bytearray(930), 124, 60, framebuf.MONO_HLSB
        )

        # timing messages
        self.showing_timed = False
        self.timed_expiration = 0

        # header status
        self.muted = False
        self.ir_status = False
        self.wifi_status = None

        # body state
        self.menu_name = None
        self.menu_items = []
        self.menu_index = 0
        # keep track of the "top" of the displayed menu so we can simulate
        # correct scrolling
        self.menu_top = 0
        self.fullscreen = True

        self.print_logo()

    def _unfullscreen(self):
        self.fullscreen = False
        self.display.fill(0)
        self._update_status()

    def _body_from(self, i):
        display_items = self.menu_items[i : i + 7]
        new_index = self.menu_index - i
        for j, item in enumerate(display_items):
            text = "{} {}".format(">" if j == new_index else " ", item)
            self.body.text(text, 0, 8 * j, 1)

    def _update_status(self):
        if self.fullscreen:
            self._unfullscreen()
        if self.showing_timed:
            return
        if self.wifi_status is None:
            wifi_msg = "???"
        elif self.wifi_status >= -45:
            wifi_msg = "."
        elif self.wifi_status >= -65:
            wifi_msg = ".o"
        else:
            wifi_msg = ".oO"

        self.header_right.fill(0)
        status = "{}{} {}".format(
            "m" if self.muted else "u", "I" if self.ir_status else "i", wifi_msg
        )

        self.header_right.text(status, 0, 0, 1)
        self.display.blit(self.header_right, 80, 0)
        self.display.show()

    def _update_body(self):
        if self.fullscreen:
            self._unfullscreen()
        self.body.fill(0)
        if self.menu_index < self.menu_top:
            # scroll up
            self.menu_top = self.menu_index
        elif self.menu_index > self.menu_top + 6:
            # scroll down
            self.menu_top += 1
        self._body_from(self.menu_top)
        self.display.blit(self.body, 0, 8)

    def _update_menu(self):
        if self.fullscreen:
            self._unfullscreen()
        self.header_left.fill(0)
        self.header_left.text(self.menu_name, 0, 0, 1)
        self.display.blit(self.header_left, 0, 0)

    def update_menu_name(self, context):
        self.menu_name = context

    def update_menu_items(self, items, index=0):
        if self.fullscreen:
            self._unfullscreen()
        # list of MenuItem
        self.menu_items = [x.get_display_text() for x in items]
        self.menu_index = index

    def finalize_body(self):
        """Finalizes and shows the body"""
        self._update_body()
        self.display.show()

    def set_ir_status(self, ir_status):
        """Sets the IR status"""
        self.ir_status = ir_status
        self._update_status()

    def toggle_ir_status(self):
        """Toggles the ir status"""
        self.ir_status = not self.ir_status
        self._update_status()

    def set_muted(self, muted):
        """Sets the mute status"""
        self.muted = muted
        self._update_status()

    def toggle_muted(self):
        """Toggles muted status"""
        self.muted = not self.muted
        self._update_status()

    def set_wifi_status(self, wifi_status):
        """Set the wifi strength or None if not connected"""
        self.wifi_status = wifi_status
        self._update_status()

    def menu_down(self):
        """Moves the menu down"""
        if self.menu_index == len(self.menu_items) - 1:
            return self.menu_index
        self.menu_index += 1
        self._update_body()
        self.finalize_body()
        return self.menu_index

    def menu_up(self):
        """Moves the menu up"""
        if self.menu_index == 0:
            return self.menu_index
        self.menu_index -= 1
        self._update_body()
        self.finalize_body()
        return self.menu_index

    def refresh(self, now):
        """Refreshes the screen if not in logo mode"""
        ret = False
        if self.fullscreen:
            return False
        if self.showing_timed:
            if now < self.timed_expiration:
                return False
            else:
                self.showing_timed = False
                ret = True
        self._update_body()
        self._update_menu()
        self._update_status()
        self.finalize_body()
        return ret

    def clear(self):
        """
        Clear the display by filling it with black pixels.
        """
        self.display.fill(0)
        self.display.show()

    def print_logo(self):
        """Prints the HushCon Logo"""
        fbuf = framebuf.FrameBuffer(bytearray(HC_LOGO), 60, 60, framebuf.MONO_HLSB)
        self.display.fill(0)
        self.display.blit(fbuf, 34, 2)
        self.display.show()
        self.fullscreen = True

    def show_timed_message(self, msgs, show_time=2000):
        """Show a timed message"""
        if isinstance(msgs, str):
            msgs = [msgs]
        now = time.ticks_ms()
        self.timed_message.fill(0)
        for i in range(self.PADDING):
            self.timed_message.rect(i, i, 124 - i * 2, 60 - i * 2, 1)
        for i, msg in enumerate(msgs[:5]):
            self.timed_message.text(
                msg, self.PADDING + self.MARGIN, self.PADDING + self.MARGIN + i * 8, 1
            )
        self.display.blit(self.timed_message, self.MARGIN, self.MARGIN)
        self.display.show()
        self.showing_timed = True
        self.timed_expiration = now + show_time
