import machine
from machine import Pin, SoftI2C
import time
import random
import neopixel
import ssd1306

# Utility Functions:
def scale_color(rgb, brightness_factor):
    """
    Scales an RGB color tuple based on the provided brightness factor.

    Parameters:
    :param rgb: Tuple of (R, G, B) values.
    :param brightness_factor: A float between 0 (off) and 1 (full brightness).
    :return: Scaled RGB tuple.
    """
    return tuple(int(val * brightness_factor) for val in rgb)

# Classes:
class NeoPixelLight:
    def __init__(self, pin, num_pixels, brightness=1.0):
        """
        Initialize the NeoPixel light with the given pin and number of pixels.
        Accounts for the ability to set the brightness.
        """
        self.np = neopixel.NeoPixel(machine.Pin(pin), num_pixels)
        self.brightness = brightness

    def set_color(self, index, color):
        """Set the color of the pixel at the specified index."""
        scaled_color = scale_color(color, self.brightness)
        self.np[index] = scaled_color
        self.np.write()

    def clear(self):
        """Clear all pixels, turning them off."""
        for i in range(7):
            self.np[i] = (0, 0, 0)
        self.np.write()

class LightShow:
    def __init__(self):
        """
        Initialize the light show with a NeoPixel light and button setup. This
        is where you set the brightness level for the light show.
        """
        self.np_light = NeoPixelLight(18, 7, brightness=0.05)
        self.setup_buttons()

    def setup_buttons(self):
        """Setup the button handlers for the different light animations."""

        Button(4, self.do_random_monkey_spaz)
        Button(14, self.do_fireworks_show)
        Button(15, self.do_grouped_fireworks_show)
        Button(13, self.do_demo)

    def do_all_off(self):
        """Turn off all LEDs."""
        self.np_light.clear()

    def _do_color_sweep(self, color):
        """Private method to sweep the LEDs with a given color."""
        for i in range(7):
            self.np_light.set_color(i, (0, 0, 0))
            time.sleep_ms(50)
            self.do_all_off()
        for i in range(7):
            self.np_light.set_color(i, color)
            time.sleep_ms(50)
            self.do_all_off()

    def _blink(self, pin):
        """Private method to blink a given pin."""
        pin.value(1)
        time.sleep_ms(50)
        pin.value(0)
        time.sleep_ms(50)
        pin.value(1)
        time.sleep_ms(50)
        pin.value(0)

    def do_cyan_sweep(self):
        """Sweep the LEDs with a cyan color."""
        self._do_color_sweep((0, 100, 100))
        self.do_all_off()

    def do_magenta_sweep(self):
        """Sweep the LEDs with a magenta color."""
        self._do_color_sweep((255, 0, 255))
        self.do_all_off()

    def do_purple_sweep(self):
        """Sweep the LEDs with a purple color."""
        self._do_color_sweep((87, 8, 255))
        self.do_all_off()

    def do_kans_wink(self):
        """Simulate Kans's winking eye."""
        print('Kans has an evil left eye. Did it wink at you?')
        evileye = machine.Pin(2, machine.Pin.OUT)
        self._blink(evileye)

    def wheel(self, pos):
        """
        Generate a color from a position between 0 and 255.

        This function uses a position value to generate an RGB color. The
        position determines the hue of the color in a way that when the
        position value ranges from 0 to 255, the function will produce a full
        spectrum of colors transitioning from red to green to blue and back to
        red.

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
        """Cycle through rainbow colors across the LEDs."""
        # Loop through a range of values from 0 to 254:
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

    def do_firework_burst(self, index, color, fade_duration_ms=100, fade_steps=10):
        """
        Simulates a firework burst on a given LED index. This is a helper
        method for the do_fireworks_show() method.

        Parameters:
        :param index: Index of the LED.
        :param color: Color tuple (R, G, B).
        :param fade_duration_ms: Total duration to fade the firework.
        :param fade_steps: Number of steps to fade the color.
        """

        # Calculate the delay between each fade step based on total duration
        # and number of steps:
        fade_delay = fade_duration_ms // fade_steps

        # Split the RGB color values for easier manipulation:
        r, g, b = color

        # Fade out the color over a series of steps:
        for i in range(fade_steps):

            # Calculate the fading factor for this step based on its position
            # in the fade sequence:
            fade_factor = (fade_steps - i) / fade_steps

            # Adjust the color's intensity based on the fade factor and set the
            # modified color:
            self.np_light.set_color(index, (int(r * fade_factor), int(g * fade_factor), int(b * fade_factor)))

            # Wait for the specified delay before proceeding to the next fade
            # step:
            time.sleep_ms(fade_delay)

        # Turn off all LEDs to complete the firework burst effect:
        self.do_all_off()

    def do_fireworks_show(self, duration_s=10, min_delay_ms=50, max_delay_ms=300):
        """
        Runs a fireworks show for the specified duration. This depends on the
        do_firework_burst() method.

        Parameters:
        :param duration_s: Total duration of the fireworks show.
        :param min_delay_ms: Minimum delay between firework bursts.
        :param max_delay_ms: Maximum delay between firework bursts.
        """
        end_time = time.ticks_ms() + duration_s * 1000

        while time.ticks_ms() < end_time:
            # Choose a random LED:
            index = random.randint(0, 6)

            # Choose a random color:
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            # Simulate a firework burst on the chosen LED with the chosen
            # color:
            self.do_firework_burst(index, color)

            # Delay for a random duration before the next burst:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

    def do_grouped_fireworks_show(self, duration_s=10, min_delay_ms=50, max_delay_ms=300):
        """
        Runs a fireworks show with grouped bursts for the specified duration.

        Parameters:
        :param duration_s: Total duration of the fireworks show.
        :param min_delay_ms: Minimum delay between firework bursts.
        :param max_delay_ms: Maximum delay between firework bursts.
        """
        end_time = time.ticks_ms() + duration_s * 1000
        groups = [
            [0, 1],      # Group for NeoPixels 1 and 2.
            [2, 3],      # Group for NeoPixels 3 and 4.
            [4, 5, 6]    # Group for NeoPixels 5, 6, and 7.
        ]

        while time.ticks_ms() < end_time:
            # Randomly select a group:
            group = random.choice(groups)

            # Choose a random bright color for the group burst:
            color = (random.randint(100, 255), random.randint(0, 255), random.randint(0, 255))

            # Simulate a firework burst for the LEDs in the chosen group:
            for index in group:
                self.do_firework_burst(index, color)

            # Delay for a random duration before the next burst:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

    def do_heartbeat(self, color=(255, 0, 0), beats_per_minute=60):
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
        for i in range(7):
            self.np_light.set_color(i, color)

        # Sleep for half the pulse duration (time the heartbeat is "on"):
        time.sleep_ms(int(pulse_duration * 500))

        # Turn off all LEDs to complete the heartbeat pulse:
        self.do_all_off()

        # Sleep for the remaining half of the pulse duration (time the
        # heartbeat is "off"):
        time.sleep_ms(int(pulse_duration * 500))

    def do_double_heartbeat(self, color=(255, 0, 0), beats_per_minute=60, pause_between_beats_ms=500):
        """
        Simulate a double heartbeat pulse with a quick second beat.

        Parameters:
        :param color: Color tuple (R, G, B) for the heartbeat.
        :param beats_per_minute: Heartbeat speed.
        :param pause_between_beats_ms: Time to pause between the first and
        second beats in milliseconds.
        """

        # Calculate the duration of one full heartbeat pulse (both on and off)
        # based on BPM:
        pulse_duration = 60 / beats_per_minute

        # First Heartbeat:
        # Illuminate all LEDs with the specified color to simulate the "beat"
        # of the heart:
        for i in range(7):
            self.np_light.set_color(i, color)

        # Sleep for half the pulse duration (time the heartbeat is "on"):
        time.sleep_ms(int(pulse_duration * 500))

        # Turn off all LEDs to complete the heartbeat pulse:
        self.do_all_off()

        # Sleep for the specified pause time between beats:
        time.sleep_ms(pause_between_beats_ms)

        # Second Heartbeat (Quick Beat):
        # Illuminate all LEDs with the specified color to simulate the "beat"
        # of the heart:
        for i in range(7):
            self.np_light.set_color(i, color)

        # Sleep for a shorter duration for the quick second beat:
        time.sleep_ms(int(pulse_duration * 250))

        # Turn off all LEDs to complete the second heartbeat pulse:
        self.do_all_off()

        # Sleep for the remaining half of the first heartbeat pulse duration:
        time.sleep_ms(int(pulse_duration * 250))

    def do_chaser(self, color=(255, 0, 0), duration_s=10):
        """
        Run a chaser light back and forth.

        Paremeters:
        :param color: Color tuple (R, G, B).
        :param duration_s: How long the pattern runs.
        """

        # Calculate when the effect should end based on the provided duration:
        end_time = time.ticks_ms() + duration_s * 1000

        # Initialize direction to determine movement (1 is forward, -1 is
        # backward):
        direction = 1

        # Starting position of the chaser light:
        position = 0

        # Continue the chaser effect until the specified duration is reached:
        while time.ticks_ms() < end_time:

            # Turn off all LEDs to prepare for the next chaser position:
            self.do_all_off()

            # Illuminate the LED at the current position with the specified
            # color:
            self.np_light.set_color(position, color)

            # Pause for a short duration before moving the chaser light:
            time.sleep_ms(100)

            # Update the chaser light's position based on its direction:
            position += direction

            # If the chaser light hits the end or the start, reverse its
            # direction:
            if position == 6 or position == 0:
                direction = -direction

    def do_random_twinkle(self, duration_s=10, min_delay_ms=50, max_delay_ms=300):
        """
        Randomly twinkle LEDs.

        Parameters:
        :param duration_s: Duration of the pattern.
        :param min_delay_ms: Minimum delay between twinkles.
        :param max_delay_ms: Maximum delay between twinkles.
        """

        # Calculate the end time for the effect based on the provided duration:
        end_time = time.ticks_ms() + duration_s * 1000

        # Continue the twinkle effect until the specified duration is reached:
        while time.ticks_ms() < end_time:

            # Randomly select an LED index to twinkle:
            index = random.randint(0, 6)

            # Generate a random color for the LED twinkle. The red component is
            # kept relatively bright to ensure visibility:
            color = (random.randint(100, 255), random.randint(0, 255), random.randint(0, 255))

            # Set the randomly chosen LED to the randomly generated color:
            self.np_light.set_color(index, color)

            # Wait for a random duration between the min and max specified
            # delays:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

            # Turn off all LEDs to simulate the end of a twinkle:
            self.do_all_off()

    def do_gradient_fade(self, start_color=(255, 0, 0), end_color=(0, 0, 255), duration_s=10):
        """
        Fade from start color to end color across all LEDs.

        Parameters:
        :param start_color: Starting color tuple (R, G, B).
        :param end_color: Ending color tuple (R, G, B).
        :param duration_s: Duration of the fade.
        """

        # Define the number of gradient steps to fade between colors:
        steps = 100

        # Calculate the delay between each step to achieve the total fade
        # duration:
        delay = duration_s / steps

        # Iterate over each step to gradually change the LED colors:
        for step in range(steps + 1):

            # Calculate the ratio of completion for the fade:
            ratio = step / steps

            # Calculate the current color for this step by linearly
            # interpolating between the start and end colors using the ratio:
            color = (
                int(start_color[0] * (1 - ratio) + end_color[0] * ratio),
                int(start_color[1] * (1 - ratio) + end_color[1] * ratio),
                int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            )

            # Set all LEDs to the calculated color for this step:
            for i in range(7):
                self.np_light.set_color(i, color)

            # Pause for the calculated delay to make the fade visible:
            time.sleep_ms(int(delay * 1000))

    def do_strobe(self, color=(0, 100, 100), duration_s=5, flashes_per_second=10):
        """
        Strobe effect with the given color.

        Parameters:
        :param color: Color tuple (R, G, B).
        :param duration_s: Duration of the effect.
        :param flashes_per_second: How many times it flashes in a second.
        """

        # Calculate the ending time based on the current time and desired
        # strobe duration:
        end_time = time.ticks_ms() + duration_s * 1000

        # Calculate the time each LED should be "on" and "off" for the desired
        # flashes per second. For instance, for 10 flashes_per_second, each LED
        # will be on for 50ms and off for 50ms:
        on_time = 1000 / (2 * flashes_per_second)

        # Continue the strobe effect until the ending time is reached:
        while time.ticks_ms() < end_time:

            # Turn on each LED with the specified color:
            for i in range(7):
                self.np_light.set_color(i, color)

            # Pause for the calculated "on" duration:
            time.sleep_ms(int(on_time))

            # Turn off all LEDs:
            self.do_all_off()

            # Pause for the calculated "off" duration, creating the strobe
            # flash:
            time.sleep_ms(int(on_time))

    def do_popcorn_effect(self, duration_s=10, pop_duration_ms=50, min_delay_ms=10, max_delay_ms=200):
        """
        Creates a popcorn effect by randomly illuminating LEDs for short
        durations, this is similiar to the fireworks effect, but doesn't depend
        on a helper method.

        Parameters:
        - duration_s: The total duration of the popcorn effect in seconds.
        - pop_duration_ms: Duration for which a 'popped' LED remains lit.
        - min_delay_ms: Minimum delay between individual LED pops.
        - max_delay_ms: Maximum delay between individual LED pops.
        """
        # Calculate the ending time based on the current time and desired
        # duration:
        end_time = time.ticks_ms() + duration_s * 1000
        # Continue the effect until the ending time is reached:
        while time.ticks_ms() < end_time:
            # Select a random LED index:
            index = random.randint(0, 6)

            # Generate a random color (RGB values between 0 and 255):
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            # Set the randomly chosen LED to the generated color:
            self.np_light.set_color(index, color)

            # Pause for the duration of the 'pop':
            time.sleep_ms(pop_duration_ms)

            # Turn off all LEDs:
            self.do_all_off()

            # Pause for a random duration between individual LED pops:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

    def do_countdown_timer(self, duration_in_seconds):
        """
        Run a countdown timer using LEDs. Each LED represents a portion of the
        total duration. As the time passes, LEDs turn off sequentially. If you
        set the duration to 7, each light will display for 1 second.

        Arguments:
        - duration_in_seconds: The total duration of the countdown in seconds.
        """
        num_pixels = len(self.np_light.np)

        # Calculate how long each LED should stay on:
        time_per_led = duration_in_seconds / num_pixels

        # Light up all LEDs at the beginning of the countdown:
        for i in range(num_pixels):
            self.np_light.set_color(i, (0, 100, 100))  # Color for the countdown.

        # Start countdown
        for i in range(num_pixels):
            time.sleep(time_per_led)
            self.np_light.set_color(i, (0, 0, 0)) # Turn off LED after its portion of time.

        # Ensure all LEDs are off at the end of the countdown:
        self.do_all_off()

    def do_monkey_roll_call(self, duration_s=10, min_delay_ms=50, max_delay_ms=300):
        """
        Runs a monkey-themed roll call show with cycling colored groups.

        Parameters:
        :param duration_s: Total duration of the show.
        :param min_delay_ms: Minimum delay between roll call bursts.
        :param max_delay_ms: Maximum delay between roll call bursts.
        """
        end_time = time.ticks_ms() + duration_s * 1000
        groups = [
            ([0, 1], (0, 100, 100)),    # Group 1 (Cyan) for NeoPixels 1 and 2.
            ([2, 3], (255, 0, 255)),    # Group 2 (Magenta) for NeoPixels 3 and 4.
            ([4, 5, 6], (87, 8, 255))   # Group 3 (Purple) for NeoPixels 5, 6, and 7.
        ]

        group_index = 0  # Starting with the first group.

        while time.ticks_ms() < end_time:
            # Monkey group are ordered to Shade (cyan), Kans (magenta) and
            # MiC (purple):
            group_indices, group_color = groups[group_index]

            # Simulate a roll call burst for the LEDs in the chosen group:
            for index in group_indices:
                self.do_firework_burst(index, group_color)

            # Delay for a random duration before the next burst:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

            # Move to the next group and wrap around if needed:
            group_index = (group_index + 1) % len(groups)

    def do_random_monkey_spaz(self, duration_s=10, min_delay_ms=50, max_delay_ms=300):
        """
        Runs a random order of the monkey-themed roll call show with colored groups.

        Parameters:
        :param duration_s: Total duration of the show.
        :param min_delay_ms: Minimum delay between roll call bursts.
        :param max_delay_ms: Maximum delay between roll call bursts.
        """
        end_time = time.ticks_ms() + duration_s * 1000
        groups = [
            ([0, 1], (0, 100, 100)),    # Group 1 (Cyan) for NeoPixels 1 and 2.
            ([2, 3], (255, 0, 255)),    # Group 2 (Magenta) for NeoPixels 3 and 4.
            ([4, 5, 6], (87, 8, 255))   # Group 3 (Purple) for NeoPixels 5, 6, and 7.
        ]

        while time.ticks_ms() < end_time:
            # Randomly select a group:
            group_indices, group_color = random.choice(groups)

            # Simulate a roll call burst for the LEDs in the chosen group:
            for index in group_indices:
                self.do_firework_burst(index, group_color)

            # Delay for a random duration before the next burst:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

    def do_monkey_spaz(self, name, group_indices, group_color, duration_s=5, blink_duration_ms=100, min_delay_ms=100, max_delay_ms=500):
        """
        Runs a light show with a swelling and blinking group.

        Parameters:
        :param name: Name of the light show (e.g., "Shade", "Kans", "MiC").
        :param group_indices: Indices of the group of NeoPixels.
        :param group_color: Color of the group in RGB format.
        :param duration_s: Total duration of the show.
        :param blink_duration_ms: Duration for which the group will blink.
        :param min_delay_ms: Minimum delay between spaz bursts.
        :param max_delay_ms: Maximum delay between spaz bursts.
        """
        end_time = time.ticks_ms() + duration_s * 1000

        while time.ticks_ms() < end_time:
            # Simulate a swelling effect by gradually increasing the
            # brightness of the group's LEDs:
            for brightness_factor in range(1, 11):
                for index in group_indices:
                    self.np_light.set_color(index, scale_color(group_color, brightness_factor / 10))
                time.sleep_ms(100)

            # Simulate blinking by turning the group off and on:
            for _ in range(blink_duration_ms // 50):
                for index in group_indices:
                    self.np_light.set_color(index, (0, 0, 0))
                time.sleep_ms(25)
                for index in group_indices:
                    self.np_light.set_color(index, group_color)
                time.sleep_ms(25)

            # Turn off all LEDs to complete the burst:
            self.do_all_off()

            # Delay for a random duration before the next burst:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

    def do_demo(self):
        """
        Runs a demo of all light show methods. Currently mapped to MiC's
        button.
        """
        print('do_countdown_timer starting...')
        self.do_countdown_timer(7)
        print('do_monkey_spaz Shade starting...')
        self.do_monkey_spaz("Shade", [0, 1], (0, 100, 100))
        print('do_monkey_spaz Kans starting...')
        self.do_monkey_spaz("kans", [2, 3], (255, 0, 255))
        print('do_monkey_spaz MiC starting...')
        self.do_monkey_spaz("mic", [4, 5, 6], (87, 8, 255))
        print('do_monkey_roll_call starting...')
        self.do_monkey_roll_call()
        print('do_random_monkey_spaz starting...')
        self.do_random_monkey_spaz()
        print('do_fireworks_show starting...')
        self.do_fireworks_show()
        print('do_cyan_sweep starting...')
        self.do_cyan_sweep()
        print('do_magenta_sweep starting...')
        self.do_magenta_sweep()
        print('do_purple_sweep starting...')
        self.do_purple_sweep()
        print('do_cyan_sweep starting...')
        self.do_cyan_sweep()
        print('do_magenta_sweep starting...')
        self.do_magenta_sweep()
        print('do_purple_sweep starting...')
        self.do_purple_sweep()
        print('do_grouped_fireworks_show starting...')
        self.do_grouped_fireworks_show()
        print('do_kans_wink starting...')
        self.do_kans_wink()
        print('do_rainbow_cycle starting...')
        self.do_rainbow_cycle()
        print('do_heartbeat starting...')
        self.do_heartbeat()
        print('do_heartbeat starting...')
        self.do_heartbeat()
        print('do_heartbeat starting...')
        self.do_heartbeat()
        print('do_chaser starting...')
        self.do_chaser()
        print('do_random_twinkle starting...')
        self.do_random_twinkle()
        print('do_gradient_fade starting...')
        self.do_gradient_fade()
        print('do_strobe starting...')
        self.do_strobe()
        print('do_popcorn_effect starting...')
        self.do_popcorn_effect()
        print('do_kans_wink starting...')
        self.do_kans_wink()
        print('Turning everything off...')
        self.do_all_off()

class SSD1306:
    """
    A class for controlling an OLED display using the SSD1306 driver.
    """

    def __init__(self, width, height, sda_pin, scl_pin):
        self.i2c = SoftI2C(sda=Pin(sda_pin), scl=Pin(scl_pin))
        self.display = ssd1306.SSD1306_I2C(width, height, self.i2c)

    def clear(self):
        self.display.fill(0)
        self.display.show()

    def show_text(self, line1='', line2='', line3='', line4='', line5='', line6='', line7=''):
        self.clear()
        self.display.text(line1, 0, 0, 1)
        self.display.text(line2, 0, 11, 1)
        self.display.text(line3, 0, 22, 1)
        self.display.text(line4, 0, 33, 1)
        self.display.text(line5, 0, 44, 1)
        self.display.text(line6, 0, 55, 1)
        self.display.show()

class Button:
    DEBOUNCE_DELAY_MS = 50

    def __init__(self, pin, callback):
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pin.irq(handler=self._pressed, trigger=machine.Pin.IRQ_FALLING)
        self.callback = callback

    def _pressed(self, pin):
        if self.debounce():
            if self.callback is not None:
                self.callback(self)

    def debounce(self):
        initial_state = self.pin.value()
        time.sleep_ms(self.DEBOUNCE_DELAY_MS)
        return initial_state == 0 and self.pin.value() == 0

class Menu(object):
    def __init__(self, options, oled, light_show, button_pins, button_functions):
        self.options = options
        self.oled = oled
        self.light_show = light_show  # Pass the light_show object here
        self.selected_option = 0
        self.buttons = [Button(pin, callback) for pin, callback in zip(button_pins, button_functions)]
        self.nav_up_button = self.buttons[0]
        self.nav_back_button = self.buttons[1]
        self.nav_enter_button = self.buttons[2]
        self.nav_back_button = self.buttons[3]

    def setup_buttons(self):
        """Setup the button handlers for the different light animations."""

        self.nav_up_button  = Button(4, self.prev_option)
        self.nav_up_button = Button(14, self.next_option)
        self.nav_enter_button = Button(15, self.execute_option)
        self.nav_back_button = Button(13, self.back_to_main)

    def _pressed(self, pin):
        if self.debounce():
            if self.callback is not None:
                self.callback(self)

    def debounce(self):
        initial_state = self.pin.value()
        time.sleep_ms(self.DEBOUNCE_DELAY_MS)
        return initial_state == 0 and self.pin.value() == 0

    def prev_option(self, button=None):
        self.selected_option = (self.selected_option - 1) % len(self.options)
        self.display_menu()

    def next_option(self, button=None):
        self.selected_option = (self.selected_option + 1) % len(self.options)
        self.display_menu()

    def execute_option(self, button=None):
        if self.selected_option == 0:
            self.oled.clear()
            self.oled.show_text("Executing:", self.options[self.selected_option])
            self.light_show.do_random_monkey_spaz()
            self.oled.clear()
        elif self.selected_option == 1:
            self.oled.clear()
            self.oled.show_text("Executing:", self.options[self.selected_option])
            self.light_show.do_popcorn_effect()
            self.oled.clear()
        elif self.selected_option == 2:
            self.oled.clear()
            self.oled.show_text("Executing:", self.options[self.selected_option])
            self.light_show.do_grouped_fireworks_show()
            self.oled.clear()
        elif self.selected_option == 3:
            self.oled.clear()
            self.oled.show_text("Executing:", self.options[self.selected_option])
            self.light_show.do_double_heartbeat()
            self.light_show.do_double_heartbeat()
            self.light_show.do_double_heartbeat()
            self.light_show.do_double_heartbeat()
            self.light_show.do_double_heartbeat()
            self.light_show.do_double_heartbeat()
            self.light_show.do_double_heartbeat()
            self.light_show.do_double_heartbeat()
            self.light_show.do_double_heartbeat()
            self.light_show.do_double_heartbeat()
            self.oled.clear()
        elif self.selected_option == 4:
            self.oled.clear()
            self.oled.show_text("Executing:", self.options[self.selected_option])
            self.light_show.do_demo()
            self.oled.clear()
        else:
            self.oled.clear()
            self.oled.show_text("Executing:", self.options[self.selected_option])
            time.sleep(2)
            self.oled.clear()
        self.display_menu()

    def back_to_main(self, button=None):
        self.selected_option = 0
        self.display_menu()

    def display_menu(self):
        lines = []
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                lines.append("* " + option)
            else:
                lines.append(option)
        while len(lines) < 7:
            lines.append('')
        self.oled.show_text(*lines)

    def run(self):
        while True:
            for button in self.buttons:
                # Changed this:
                if button.pin.value() == 0 and not button.debounce():
                    if button.callback is not None:
                        button.callback()

            time.sleep(0.2)

# Usage:

# Initialize OLED display:
oled = SSD1306(128, 64, sda_pin=5, scl_pin=23)

# Create NeoPixelLight instance:
np_light = NeoPixelLight(18, 7, brightness=0.05)

# Create LightShow instance and pass NeoPixelLight instance:
light_show = LightShow()

# List of menu options and button pins:
menu_options = ["1. Monkey Spaz", "2. Popcorn", "3. Fireworks", "4. Heartbeat", "5. Demo", "Back"]
button_pins = [4, 14, 15, 13]

# Instantiate the Menu class with the menu_options list:
menu = Menu(menu_options, oled, light_show, button_pins, [None]*len(button_pins))

# Map buttons to their functions:
button_functions = [
    menu.prev_option,        # Up button.
    menu.next_option,        # Down button.
    menu.execute_option,     # Enter button.
    menu.back_to_main        # Back button.
]

# Assign button functions to the menu's buttons:
for i in range(len(button_pins)):
    menu.buttons[i].callback = button_functions[i]

menu.display_menu()         # Initial menu display.
