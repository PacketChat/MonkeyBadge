"""konami code challenge"""
import time
import machine
from machine import Pin, SoftI2C
import ssd1306
import framebuf
import neopixel

KONAMI_LOGO = bytearray(b'\x00\x18\x00\x00x\x00\x00\xf8\x00\x01\xf8\x00\x01'
                        b'\xf8`\x01\xf9\xe0\x03\xfb\xe0\x03\xc7\xe0\x07\x07'
                        b'\xe0\x0e\x07\xe0>\x0f\xe0\xfe\x0f\x00\xfc\x1c\x00'
                        b'\xfc8\x00\xfc\xf8\x00\xfb\xf8\x00\xe3\xf0\x00\x83'
                        b'\xf0\x00\x03\xf0\x00\x03\xe0\x00\x03\x80\x00\x02'
                        b'\x00\x00')
KONAMI_DIM = (22, 19)


LEFT = bytearray(b'\x00\x18<Z\x18\x18\x18\x00')
RIGHT = bytearray(b'\x00\x18\x18\x18Z<\x18\x00')
UP = bytearray(b'\x00\x08\x04~~\x04\x08\x00')
DOWN = bytearray(b'\x00\x10 ~~ \x10\x00')
ENTER = bytearray(b'\x108|\x10\x10\x12\x1e\x00')

def do_heartbeat(np, color=(180, 0, 0), beats_per_minute=60):
    """
    Simulate a heartbeat pulse with the given color.

    Parameters:
    :param color: Color tuple (R, G, B).
    :param beats_per_minute: Heartbeat speed.
    """

    # Calculate the duration of one full heartbeat pulse (both on and off)
    # based on BPM:
    pulse_duration = 60 / beats_per_minute

    # Illuminate all LEDs with the specified color to simulate the "beat"
    # of the heart:
    np.fill(color)
    np.write()

    # Sleep for half the pulse duration (time the heartbeat is "on"):
    time.sleep_ms(int(pulse_duration * 500))

    # Turn off all LEDs to complete the heartbeat pulse:
    np.fill((0, 0, 0))
    np.write()

    # Sleep for the remaining half of the pulse duration (time the
    # heartbeat is "off"):
    time.sleep_ms(int(pulse_duration * 500))



# Classes:
class Button:
    """
    A class for initializing buttons and handling button press events with
    debounce logic.
    """

    # The time in milliseconds for button debounce.
    DEBOUNCE_DELAY_MS = 50

    def __init__(self, pin, callback):
        """
        Initialize the button with the given pin and a callback function to
        execute on button press.

        :param pin: The pin connected to the button.
        :param callback: The function to be called when the button is pressed.
        """
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pin.irq(handler=self._pressed, trigger=machine.Pin.IRQ_FALLING)
        self.callback = callback

    def _pressed(self, pin):
        """
        Private method to handle button press with debouncing.

        This method is automatically called when the button is pressed.
        It checks for button debouncing and triggers the callback if the press
        is valid.
        """
        if self.debounce():
            # state = machine.disable_irq()
            self.callback()
            # machine.enable_irq(state)
            # Wait for the button to be released before allowing another press:
            while self.pin.value() == 0:
                pass

    def debounce(self):
        """
        Perform button debouncing to ensure a valid button press event.

        This method helps eliminate false positives caused by button bouncing.
        :return: True if the button press is valid, False otherwise.
        """
        initial_state = self.pin.value()
        time.sleep_ms(self.DEBOUNCE_DELAY_MS)
        # Check if the button is still pressed and its state hasn't changed
        # during debounce delay:
        return initial_state == 0 and self.pin.value() == 0

class SSD1306:
    """
    A class for controlling an OLED display using the SSD1306 driver.
    """

    def __init__(self, width, height, sda_pin, scl_pin):
        """
        Initialize the OLED display with the given dimensions and I2C pins.

        :param width: Width of the display in pixels.
        :param height: Height of the display in pixels.
        :param sda_pin: The SDA pin for I2C communication.
        :param scl_pin: The SCL pin for I2C communication.
        """
        self.width = width
        self.height = height
        self.i2c = SoftI2C(sda=Pin(sda_pin), scl=Pin(scl_pin))
        self.display = ssd1306.SSD1306_I2C(width, height, self.i2c)
        # self.swap = framebuf.FrameBuffer(bytearray(width * height), width, height)

    def clear(self):
        """
        Clear the display by filling it with black pixels and updating the
        display.
        """
        self.display.fill(0)
        self.display.show()

    def text(self, *args, **kwargs):
        self.display.text(*args, **kwargs)

    def fill(self, *args, **kwargs):
        self.display.fill(*args, **kwargs)

    def show(self):
        self.display.show()

    def blit(self, *args, **kwargs):
        self.display.blit(*args, **kwargs)

    def blink(self, n=10, sleep_time=150):
        invert = 0
        for _ in range(n):
            invert ^= 1
            self.display.invert(invert)
            time.sleep_ms(sleep_time)

class ExtendedBuffer(framebuf.FrameBuffer):
    CHAR_HEIGHT = 8
    CHAR_WIDTH = 8

    SCREEN_WIDTH = 128
    SCREEN_HEIGHT = 64

    def _center(self, text, row, color):
        tlen = len(text) * self.CHAR_WIDTH
        x = 0 if tlen > self.SCREEN_WIDTH else (self.SCREEN_WIDTH - tlen) // 2
        self.text(text, x, row * self.CHAR_HEIGHT, color)

    def _left(self, text, row, color):
        self.text(text, 0, row * self.CHAR_HEIGHT, color)

    def _right(self, text, row, color):
        tlen = len(text) * self.CHAR_WIDTH
        x = 0 if tlen > self.SCREEN_WIDTH else (self.SCREEN_WIDTH - tlen)
        self.text(text, x, row * self.CHAR_HEIGHT, color)

    def enter(self, top_left, color):
        x, y = top_left
        tbuf = framebuf.FrameBuffer(bytearray(8), 8, 8, framebuf.MONO_VLSB)
        tbuf.fill(color ^ 1)
        tbuf.pixel(5, 1, color)
        for i in range(4):
            tbuf.pixel(6, i + 1, color)
        for i in range(7):
            tbuf.pixel(i, 4, color)
        for i in range(5):
            tbuf.pixel(2, i + 2, color)
        for i in range(3):
            tbuf.pixel(1, i + 3, color)
        self.blit(tbuf, x, y)

    def arrow(self, direction, top_left, color):
        tlx, tly = top_left
        if direction in ['left', 'right']:
            self.hline(tlx + 1, tly + 3, 6, color)
            self.hline(tlx + 1, tly + 4, 6, color)

        if direction in ['up', 'down']:
            self.vline(tlx + 3, tly + 1, 6, color)
            self.vline(tlx + 4, tly + 1, 6, color)

        if direction in ['left', 'up']:
            self.line(tlx + 1, tly + 3, tlx + 3, tly + 1, color)
        if direction in ['right', 'down']:
            self.line(tlx + 6, tly + 4, tlx + 4, tly + 6, color)
        if direction in ['left', 'down']:
            self.line(tlx + 1, tly + 4, tlx + 3, tly + 6, color)
        if direction in ['right', 'up']:
            self.line(tlx + 4, tly + 1, tlx + 6, tly + 3, color)


    def symbol(self, name, top_left, color):
        if name in ['left', 'right', 'up', 'down']:
            self.arrow(name, top_left, color)
        elif name == 'enter':
            self.enter(top_left, color)
        else:
            self.text(name, *top_left, color)

    def text_row(self, text, row, position, color):
        func = self._left
        if position == 'right':
            func = self._right
        elif position == 'center':
            func = self._center
        func(text, row, color)


class Konami:
    KEYS = ['left', 'right', 'up', 'down', 'A', 'B', 'enter']

    def __init__(self):
        self._won = False
        self.code = []
        self.idx = 3
        self.display = SSD1306(128, 64, sda_pin=5, scl_pin=23)
        self.display.display.contrast(5)
        # since a single byte encapsulates 8 pixels then a bytearray of width
        # gives a single character line of 8x8 pixels per character
        self.code_view = ExtendedBuffer(
                bytearray(self.display.width),
                self.display.width,
                ExtendedBuffer.CHAR_HEIGHT * 1,
                framebuf.MONO_VLSB
        )

        selection_height = (
                self.display.height - (ExtendedBuffer.CHAR_HEIGHT * 2)
        )
        self.selection = ExtendedBuffer(
                bytearray(self.display.width * selection_height),
                self.display.width // 2,
                selection_height,
                framebuf.MONO_VLSB
        )

        self._buttons = []
        self._hook_buttons()
        self.refresh()

    def _hook_buttons(self):
        self._buttons.append(Button(4, self._button_up))
        self._buttons.append(Button(14, self._button_down))
        self._buttons.append(Button(13, self._button_enter))
        self._buttons.append(Button(15, self._button_enter))

    def _button_up(self, *_args):
        """Callback for up button"""
        self.idx = max(0, self.idx - 1)
        self.refresh()

    def _button_down(self, *_args):
        """Callback for down button"""
        self.idx = min(len(self.KEYS), self.idx + 1)
        self.refresh()

    def _button_enter(self, *_args):
        """Callback for 'enter' button"""
        self.code.append(self.KEYS[self.idx])
        if not self._code_complete():
            self.refresh()

    def _code_complete(self):
        """Checks if the konami code has been entered
            Returns true if code hasn't been completed yet and False
        """

        konami = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right',
                  'B', 'A', 'enter']
        clen = len(self.code)
        if konami[:clen] != self.code:
            self.code = []
            return False
        if clen == len(konami):
            # self._unhook_buttons()
            self._win_screen()
            return True
        return False

    def _win_screen(self):
        self._won = True
        tbuf = ExtendedBuffer(bytearray(self.display.width * self.display.height // 8),
                              self.display.width, self.display.height,
                              framebuf.MONO_VLSB)
        self.display.fill(0)
        tbuf.fill(0)

        for i in range(0, self.display.height, 2):
            tbuf.fill_rect(0, i * 8, self.display.width, 8, 1)
        for button in self._buttons:
            button.pin.irq(lambda x: (), machine.Pin.IRQ_FALLING)
        tbuf.text_row('WINNER', 0, 'left', 0)
        tbuf.text_row('WINNER', 2, 'right', 0)
        tbuf.text_row('CHICKEN', 4, 'left', 0)
        tbuf.text_row('DINNER', 6, 'right', 0)
        self.display.blit(tbuf, 0, 0)
        self.display.show()
        time.sleep_ms(1500)

    def _refresh_selection(self):
        self.selection.fill(0)
        selected_key = self.KEYS[self.idx]
        shown_keys = self.KEYS[max(self.idx - 2, 0):self.idx + 6]
        for i, key in enumerate(shown_keys):
            color = 1
            if key == selected_key:
                self.selection.fill_rect(0, i * 8,
                                         self.display.width, 8, 1)
                color = 0
            self.selection.symbol(key, (0, i * 8), color)
        # blit two rows down
        self.display.blit(self.selection, 0, 8 * 2)

    def _refresh_code_view(self):
        self.code_view.fill(0)
        for i, c in enumerate(self.code):
            self.code_view.symbol(c, (i * 8, 0), 1)
        # blit one row down
        self.display.blit(self.code_view, 0, 8)


    @property
    def won(self):
        return self._won

    def refresh(self):
        self.display.fill(0)
        self.display.text('Enter Code:', 0, 0)
        self._refresh_code_view()
        self._refresh_selection()

        # add konami logo to bottom right
        kbuf = ExtendedBuffer(KONAMI_LOGO, *KONAMI_DIM, framebuf.MONO_HLSB)
        self.display.blit(kbuf,
                          self.display.width - KONAMI_DIM[0],
                          self.display.height - KONAMI_DIM[1])
        self.display.show()


def main():
    """Entry function"""
    np = neopixel.NeoPixel(machine.Pin(18), 7)

    k = Konami()
    while True:
        do_heartbeat(np)
        if k.won:
            np.fill((0, 0, 0))
            np.write()
            break


if __name__ == '__main__':
    main()
