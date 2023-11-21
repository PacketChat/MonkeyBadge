import micropython
from machine import Pin
import uasyncio as asyncio
import utime

class ButtonHandler:
    """
    ButtonHandler class
    """
    def __init__(self,
                 cb_left_up,
                 cb_left_down,
                 cb_center,
                 cb_right,
                 debounce_time=250):
        """
        ButtonHandler initializer function

        :param button_pins: List of button pins
        :param debounce_time: Debounce time in milliseconds
        """
        self.last_pressed = [0] * 4
        self.debounce_time = debounce_time

        self.left_up = Pin(4, Pin.IN, Pin.PULL_UP)
        self.left_down = Pin(14, Pin.IN, Pin.PULL_UP)
        self.center = Pin(15, Pin.IN, Pin.PULL_UP)
        self.right = Pin(13, Pin.IN, Pin.PULL_UP)

        self.left_up.irq(trigger=Pin.IRQ_FALLING,
                         handler=self._generic_callback(cb_left_up, 0))
        self.left_down.irq(trigger=Pin.IRQ_FALLING,
                           handler=self._generic_callback(cb_left_down, 1))
        self.center.irq(trigger=Pin.IRQ_FALLING,
                        handler=self._generic_callback(cb_center, 2))
        self.right.irq(trigger=Pin.IRQ_FALLING,
                       handler=self._generic_callback(cb_right, 3))

    def _generic_callback(self, callback, idx):
        def _f(*args):
            current_time = utime.ticks_ms()
            diff = utime.ticks_diff(current_time, self.last_pressed[idx])
            if diff > self.debounce_time:
                self.last_pressed[idx] = current_time
                if callback:
                    callback()

        def _g(*args):
            micropython.schedule(_f, None)

        return _g
