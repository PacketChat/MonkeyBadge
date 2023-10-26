import machine
import uasyncio as asyncio
import utime

class ButtonHandler:
    def __init__(self, button_pins, debounce_time=250):
        self.button_pins = button_pins
        self.buttons = [machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP) for pin in button_pins]
        self.last_pressed = [0] * len(button_pins)
        self.debounce_time = debounce_time
        self.callback = None

        for idx, button in enumerate(self.buttons):
            button.irq(trigger=machine.Pin.IRQ_FALLING, handler=lambda p, idx=idx: self._generic_callback(idx))

    def set_callback(self, callback):
        self.callback = callback

    def _generic_callback(self, button_idx):
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, self.last_pressed[button_idx]) > self.debounce_time:
            self.last_pressed[button_idx] = current_time
            if self.callback:
                self.callback(button_idx)

    async def check_buttons(self):
        while True:
            for idx, button in enumerate(self.buttons):
                if button.value() == 0:
                    self._generic_callback(idx)
            await asyncio.sleep(0.1)  # non-blocking wait for 100ms