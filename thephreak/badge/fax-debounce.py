import machine, neopixel, time, network
from machine import Pin

"""
The debounce logic in this code is good to go. The debounce() function first
stores the initial state of the button, waits for the debounce delay, and then
checks if the initial state was low and the current state is still low. This
helps ensure that a button press is only registered if the button remains
pressed and stable during the debounce delay.
"""

# Neopixel setup:
np = neopixel.NeoPixel(machine.Pin(18), 7)

# Sleep value:
sleep_value = 50

def do_all_off():
    """Turn off all LEDs."""
    for i in range(7):
      np[i] = (0, 0, 0)
      np.write()

def wheel(self, pos):
    """
    Generate a color from a position between 0 and 255.

    This function uses a position value to generate an RGB color. The position
    determines the hue of the color in a way that when the position value
    ranges from 0 to 255, the function will produce a full spectrum of colors
    transitioning from red to green to blue and back to red.

    Parameters:
    :param pos: An integer value between 0 and 255 inclusive.
    :return: RGB color tuple (R, G, B).
    """

    # When position is in the range 0-84, transition from green to red:
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    # When position is in the range 85-169, transition from red to blue:
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    # When position is in the range 170-255, transition from blue to green:
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def do_rainbow_cycle(self):
    """
    Loop through a range of values from 0 to 254.
    """
    for j in range(255):
        # Loop through each of the 7 LEDs:
        for i in range(7):
            # Generate a rainbow color for the current LED:
            color = self.wheel((i + j) & 255)
            # Set the LED's color to the generated rainbow color:
            self.np_light.set_color(i, color)
        # Pause for 10 ms to create a smooth transition between colors:
        time.sleep_ms(10)
    self.do_all_off() # Turn off all LEDs after cycling through the rainbow.

def do_purple_sweep():
    """
    A left to right sweep of purple:
    """
    for i in range(7):
        np[i] = (0, 0, 0)
        np.write()
        time.sleep_ms(sleep_value)
    for i in range(7):
        np[i] = (87, 8, 255)
        np.write()
        time.sleep_ms(sleep_value)

def do_cyan_sweep():
    """
    A left to right sweep of cyan:
    """
    for i in range(7):
        np[i] = (0, 0, 0)
        np.write()
        time.sleep_ms(sleep_value)
    for i in range(7):
        np[i] = (0, 100, 100)
        np.write()
        time.sleep_ms(sleep_value)

def do_magenta_sweep():
    """
    A left to right sweep of magenta.
    """
    for i in range(7):
        np[i] = (0, 0, 0)
        np.write()
        time.sleep_ms(sleep_value)
    for i in range(7):
        np[i] = (255, 0, 255)
        np.write()
        time.sleep_ms(sleep_value)

def do_kans_wink():
    """
    Wink the blue LED on Canz's left eye.
    """
    print ('Canz has an evil left eye. Did it wink at you?')
    evileye = Pin(2, Pin.OUT)
    evileye.value(1)
    time.sleep_ms(sleep_value)
    evileye.value(0)
    time.sleep_ms(sleep_value)
    evileye.value(1)
    time.sleep_ms(sleep_value)
    evileye.value(0)

# Buttons:
# GPIO's are as follows:
# UP=4, DN=14, CANZ=15, MIC=13

# Debounce delay in milliseconds:
DEBOUNCE_DELAY_MS = 50

# Improved debounce function:
def debounce(pin):
    initial_state = pin.value()
    time.sleep_ms(DEBOUNCE_DELAY_MS)
    return initial_state == 0 and pin.value() == 0

# Improved Button handler functions to check button release after execution:
def up_pressed(pin):
    if debounce(pin):
        print('Up button pressed')
        do_cyan_sweep()
        do_all_off()
        while pin.value() == 0:  # Wait for button release.
            pass

def dn_pressed(pin):
    if debounce(pin):
        print('Down button pressed')
        do_rainbow_cycle()
        do_all_off()
        while pin.value() == 0:  # Wait for button release.
            pass

def kans_pressed(pin):
    if debounce(pin):
        print('Canz button pressed')
        do_magenta_sweep()
        do_all_off()
        while pin.value() == 0:  # Wait for button release.
            pass

def mic_pressed(pin):
    if debounce(pin):
        print('Mic button pressed')
        do_purple_sweep()
        do_all_off()
        while pin.value() == 0:  # Wait for button release.
            pass

# Pins setup:
p_up = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
p_dn = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
p_kans = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
p_mic = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)

# IRQ setup:
p_up.irq(handler=up_pressed, trigger=machine.Pin.IRQ_FALLING)
p_dn.irq(handler=dn_pressed, trigger=machine.Pin.IRQ_FALLING)
p_kans.irq(handler=kans_pressed, trigger=machine.Pin.IRQ_FALLING)
p_mic.irq(handler=mic_pressed, trigger=machine.Pin.IRQ_FALLING)

# Display a light show:
do_cyan_sweep()
do_magenta_sweep()
do_purple_sweep()
do_cyan_sweep()
do_magenta_sweep()
do_purple_sweep()
do_kans_wink()
do_all_off()
