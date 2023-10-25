import machine
import uasyncio as asyncio
import utime

class ButtonHandler:
    def __init__(self, button_pins, debounce_time=300):
        self.button_pins = button_pins
        self.buttons = [machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP) for pin in button_pins]
        self.last_pressed = [0] * len(button_pins)
        self.debounce_time = debounce_time

        for idx, button in enumerate(self.buttons):
            button.irq(trigger=machine.Pin.IRQ_FALLING, handler=lambda p, idx=idx: self._generic_callback(idx))

    def _generic_callback(self, button_idx):
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, self.last_pressed[button_idx]) > self.debounce_time:
            self.last_pressed[button_idx] = current_time
            print(f"Button press detected on pin: {self.button_pins[button_idx]}")

    async def check_buttons(self):
        while True:
            for idx, button in enumerate(self.buttons):
                if button.value() == 0:
                    self._generic_callback(idx)
            await asyncio.sleep(0.1)  # non-blocking wait for 100ms
