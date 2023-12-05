import _thread as thread
import machine
import math
import neopixel
import random
import time


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

    def clear(self):
        """Clear all pixels, turning them off."""
        for i in range(7):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def set(self, index, color):
        """Set the color of the pixel at the specified index."""
        scaled_color = scale_color(color, self.brightness)
        self.np[index] = scaled_color

    def set_color(self, index, color):
        """Set the color of the pixel using _set() and write."""
        self.set(index, color)
        self.np.write()

    def fill(self, color):
        self.np.fill(scale_color(color, self.brightness))
        self.np.write()


class LEDHandler:
    def __init__(self):
        """
        Initialize the light show with a NeoPixel light. This is where you set the brightness level for the light show.
        """
        self.np_light = NeoPixelLight(18, 7, brightness=0.8)
        self.current_show = thread.allocate_lock()

        self.lightshow_dict = {
            "do_cyan_sweep": "Cyan Sweep",
            "do_magenta_sweep": "Magenta Sweep",
            "do_purple_sweep": "Purple Sweep",
            "do_kans_wink": "Kans Wink",
            "do_rainbow_cycle": "Rainbow",
            "do_fireworks_show": "Fireworks I",
            "do_grouped_fireworks_show": "Fireworks II",
            "do_heartbeat": "Heartbeat",
            "do_double_heartbeat": "Dbl Heartbeat",
            "do_chaser": "Chaser",
            "do_random_twinkle": "Random Twinkle",
            "do_gradient_fade": "Gradient Fade",
            "do_strobe": "Strobe",
            "do_popcorn_effect": "Popcorn",
            "do_countdown_timer": "Countdown",
            "do_monkey_roll_call": "Roll Call",
            "do_random_monkey_spaz": "Random Spaz",
            "do_predator_countdown": "Predator",
            "do_predator_purple_magenta_cyan_countdown": "PMC Predator",
            "do_slot_machine_effect": "Slot Machine",
            "do_jackpot_effect": "Jackpot",
            "do_boot_sequence": "Boot Sequence",
        }

        # Initialize an empty list to store selected lightshows:
        self.selected_lightshows = []

        while len(self.selected_lightshows) < 5:
            random_key = random.choice(list(self.lightshow_dict.keys()))
            if random_key not in self.selected_lightshows:
                self.selected_lightshows.append(random_key)

    def set_led_lights(self, lights_func, *args):
        func = getattr(self, lights_func)
        if self.current_show.locked():
            return False
        thread.stack_size(1024 * 8)
        thread.start_new_thread(self._lock_wrapped_t, [func] + list(args))
        return True

    def _lock_wrapped_t(self, func, *args):
        self.current_show.acquire()
        func(*args)
        self.current_show.release()

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
        """Simulate Canz's winking eye."""
        print("Canz has an evil left eye. Did it wink at you?")
        evileye = machine.Pin(2, machine.Pin.OUT)
        self._blink(evileye)

    def do_rainbow_cycle(self):
        """Cycle through rainbow colors across the LEDs at a fixed speed."""

        # Internal helper function to generate a color from a position:
        def wheel(pos):
            if pos < 85:
                return (pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                return (255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                return (0, pos * 3, 255 - pos * 3)

        # Fixed speed for the rainbow cycle (can adjust as needed):
        speed = 10

        # Loop through a range of values from 0 to 254:
        for j in range(255):
            # Loop through each of the 7 LEDs:
            for i in range(7):
                # Generate a rainbow color for the current LED:
                color = wheel((i + j) & 255)
                # Set the LED's color to the generated rainbow color:
                self.np_light.set_color(i, color)
            # Pause for a smooth transition between colors:
            time.sleep_ms(speed)

        self.do_all_off()  # Turn off all LEDs after cycling through the rainbow.

    def do_fireworks_show(self):
        """Runs a fireworks show with hardcoded duration and delays."""

        # Predefined values for the fireworks show:
        duration_s = 10
        min_delay_ms = 50
        max_delay_ms = 300
        fade_duration_ms = 100
        fade_steps = 10

        # Inner function to simulate a firework burst:
        def do_firework_burst(index, color):
            fade_delay = fade_duration_ms // fade_steps
            r, g, b = color
            for i in range(fade_steps):
                fade_factor = (fade_steps - i) / fade_steps
                self.np_light.set_color(
                    index,
                    (int(r * fade_factor), int(g * fade_factor), int(b * fade_factor)),
                )
                time.sleep_ms(fade_delay)
            self.do_all_off()

        # Running the fireworks show
        end_time = time.ticks_ms() + duration_s * 1000
        while time.ticks_ms() < end_time:
            index = random.randint(0, 6)
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            do_firework_burst(index, color)
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

    def do_grouped_fireworks_show(self):
        """Runs a grouped fireworks show with hardcoded duration and delays."""

        # Predefined values for the grouped fireworks show:
        duration_s = 10
        min_delay_ms = 50
        max_delay_ms = 300
        fade_duration_ms = 100
        fade_steps = 10

        # Internal helper function to simulate a firework burst:
        def do_firework_burst(index, color):
            fade_delay = fade_duration_ms // fade_steps
            r, g, b = color
            for i in range(fade_steps):
                fade_factor = (fade_steps - i) / fade_steps
                self.np_light.set_color(
                    index,
                    (int(r * fade_factor), int(g * fade_factor), int(b * fade_factor)),
                )
                time.sleep_ms(fade_delay)
            self.do_all_off()

        # Group definitions:
        groups = [
            [0, 1],  # Group for NeoPixels 1 and 2.
            [2, 3],  # Group for NeoPixels 3 and 4.
            [4, 5, 6],  # Group for NeoPixels 5, 6, and 7.
        ]

        # Running the grouped fireworks show:
        end_time = time.ticks_ms() + duration_s * 1000
        while time.ticks_ms() < end_time:
            group = random.choice(groups)
            color = (
                random.randint(100, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            for index in group:
                do_firework_burst(index, color)
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

    def do_heartbeat(self):
        """Simulates a heartbeat pulse with a predefined color and speed."""

        # Predefined color and heartbeat speed:
        color = (255, 0, 0)  # Red color.
        beats_per_minute = 60  # Heartbeat speed in beats per minute.

        # Calculate the duration of one full heartbeat pulse (both on and off)
        # based on BPM:
        pulse_duration = 60 / beats_per_minute

        # Illuminate all LEDs with the specified color to simulate the "beat"
        # of the heart:
        for i in range(7):  # Assuming 7 LEDs
            self.np_light.set_color(i, color)

        # Sleep for half the pulse duration (time the heartbeat is "on"):
        time.sleep_ms(int(pulse_duration * 500))

        # Turn off all LEDs to complete the heartbeat pulse:
        self.do_all_off()

        # Sleep for the remaining half of the pulse duration (time the
        # heartbeat is "off"):
        time.sleep_ms(int(pulse_duration * 500))

    def do_double_heartbeat(self):
        """
        Simulate a double heartbeat pulse with a quick second beat.
        """

        # Predefined color, beats per minute and pause values:
        color = (255, 0, 0)
        beats_per_minute = 60
        pause_between_beats_ms = 50

        # Calculate the duration of one full heartbeat pulse (both on and off)
        # based on BPM:
        pulse_duration = 60 / beats_per_minute

        # First Heartbeat:
        # Illuminate all LEDs with the specified color to simulate the "beat"
        # of the heart:
        self.np_light.fill(color)

        # Sleep for half the pulse duration (time the heartbeat is "on"):
        time.sleep_ms(int(pulse_duration * 500))

        # Turn off all LEDs to complete the heartbeat pulse:
        self.do_all_off()

        # Sleep for the specified pause time between beats:
        time.sleep_ms(pause_between_beats_ms)

        # Second Heartbeat (Quick Beat):
        # Illuminate all LEDs with the specified color to simulate the "beat"
        # of the heart:
        self.np_light.fill(color)

        # Sleep for a shorter duration for the quick second beat:
        time.sleep_ms(int(pulse_duration * 250))

        # Turn off all LEDs to complete the second heartbeat pulse:
        self.do_all_off()

        # Sleep for the remaining half of the first heartbeat pulse duration:
        time.sleep_ms(int(pulse_duration * 250))

    def do_chaser(self):
        """
        Run a chaser light back and forth.
        """

        # Predefined color and duration:
        color = (255, 0, 0)
        duration_s = 10

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

        # Turn off all LEDs to complete the second heartbeat pulse:
        self.do_all_off()

    def do_random_twinkle(self):
        """
        Randomly twinkle LEDs.
        """
        duration_s = 10  # Duration of the pattern.
        min_delay_ms = 50  # Minimum delay between twinkles.
        max_delay_ms = 300  # Maximum delay between twinkles.

        # Calculate the end time for the effect based on the provided duration:
        end_time = time.ticks_ms() + duration_s * 1000

        # Continue the twinkle effect until the specified duration is reached:
        while time.ticks_ms() < end_time:
            # Randomly select an LED index to twinkle:
            index = random.randint(0, 6)

            # Generate a random color for the LED twinkle. The red component is
            # kept relatively bright to ensure visibility:
            color = (
                random.randint(100, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )

            # Set the randomly chosen LED to the randomly generated color:
            self.np_light.set_color(index, color)

            # Wait for a random duration between the min and max specified
            # delays:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

            # Turn off all LEDs to simulate the end of a twinkle:
            self.do_all_off()

    def do_gradient_fade(self):
        """
        Fade from start color to end color across all LEDs.
        """

        # Predefined start and end colors, and duration
        start_color = (255, 0, 0)  # Starting color: Red
        end_color = (0, 0, 255)  # Ending color: Blue
        duration_s = 10  # Duration of the fade in seconds

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
                int(start_color[2] * (1 - ratio) + end_color[2] * ratio),
            )

            # Set all LEDs to the calculated color for this step:
            for i in range(7):
                self.np_light.set_color(i, color)

            # Pause for the calculated delay to make the fade visible:
            time.sleep_ms(int(delay * 1000))

        # Turn off all LEDs to simulate the end of the gradient fade:
        self.do_all_off()

    def do_strobe(self):
        """
        Strobe effect with the given color.
        """

        # Predefined color, duration and flashes per second:
        color = (0, 100, 100)  # Color tuple (R, G, B).
        duration_s = 5  # Duration of the effect.
        flashes_per_second = 10  # How many times it flashes in a second.

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

    def do_popcorn_effect(self):
        """
        Creates a popcorn effect by randomly illuminating LEDs for short
        durations, this is similiar to the fireworks effect, but doesn't depend
        on a helper function.
        """

        # Predefined durations and delays:
        duration_s = 10  # The total duration of the popcorn effect in seconds.
        pop_duration_ms = 50  # Duration for which a 'popped' LED remains lit.
        min_delay_ms = 10  # Minimum delay between individual LED pops.
        max_delay_ms = 200  # Maximum delay between individual LED pops.

        # Calculate the ending time based on the current time and desired
        # duration:
        end_time = time.ticks_ms() + duration_s * 1000
        # Continue the effect until the ending time is reached:
        while time.ticks_ms() < end_time:
            # Select a random LED index:
            index = random.randint(0, 6)

            # Generate a random color (RGB values between 0 and 255):
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )

            # Set the randomly chosen LED to the generated color:
            self.np_light.set_color(index, color)

            # Pause for the duration of the 'pop':
            time.sleep_ms(pop_duration_ms)

            # Turn off all LEDs:
            self.do_all_off()

            # Pause for a random duration between individual LED pops:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

    def do_countdown_timer(self):
        """
        Run a countdown timer using LEDs. Each LED represents a portion of the
        total duration. As the time passes, LEDs turn off sequentially. If you
        set the duration to 7, each light will display for 1 second.
        """
        # Predefined duration:
        duration_in_seconds = 7  # The total duration of the countdown in seconds.

        num_pixels = len(self.np_light.np)

        # Calculate how long each LED should stay on:
        time_per_led = duration_in_seconds / num_pixels

        # Light up all LEDs at the beginning of the countdown:
        for i in range(num_pixels):
            self.np_light.set_color(i, (0, 100, 100))  # Color for the countdown.

        # Start countdown
        for i in range(num_pixels):
            time.sleep(time_per_led)
            # Turn off LED after its portion of time:
            self.np_light.set_color(i, (0, 0, 0))

        # Ensure all LEDs are off at the end of the countdown:
        self.do_all_off()

    def do_monkey_roll_call(self):
        """
        Runs a monkey-themed roll call show with cycling colored groups.
        """

        # Predefined duration and delays:
        duration_s = 10  # Total duration of the show.
        min_delay_ms = 50  # Minimum delay between roll call bursts.
        max_delay_ms = 300  # Maximum delay between roll call bursts.

        # Predefined values for the fireworks show:
        duration_s = 10
        min_delay_ms = 50
        max_delay_ms = 300
        fade_duration_ms = 100
        fade_steps = 10

        # Inner function to simulate a firework burst:
        def do_firework_burst(index, color):
            fade_delay = fade_duration_ms // fade_steps
            r, g, b = color
            for i in range(fade_steps):
                fade_factor = (fade_steps - i) / fade_steps
                self.np_light.set_color(
                    index,
                    (int(r * fade_factor), int(g * fade_factor), int(b * fade_factor)),
                )
                time.sleep_ms(fade_delay)
            self.do_all_off()

        end_time = time.ticks_ms() + duration_s * 1000

        groups = [
            ([0, 1], (87, 8, 255)),  # Group 1 (Purple) for NeoPixels 1 and 2.
            ([2, 3], (255, 0, 255)),  # Group 2 (Magenta) for NeoPixels 3 and 4.
            ([4, 5, 6], (0, 100, 100)),  # Group 3 (Cyan) for NeoPixels 5, 6, and 7.
        ]

        group_index = 0  # Starting with the first group.

        while time.ticks_ms() < end_time:
            # Monkey group are ordered to Shade (purple), Kans (magenta) and
            # MiC (cyan):
            group_indices, group_color = groups[group_index]

            # Simulate a roll call burst for the LEDs in the chosen group:
            for index in group_indices:
                do_firework_burst(index, group_color)

            # Delay for a random duration before the next burst:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

            # Move to the next group and wrap around if needed:
            group_index = (group_index + 1) % len(groups)

    def do_random_monkey_spaz(self):
        """
        Runs a random order of the monkey-themed roll call show with colored
        groups.
        """

        # Predefined duration and delays:
        duration_s = 10  # Total duration of the show.
        min_delay_ms = 50  # Minimum delay between roll call bursts.
        max_delay_ms = 300  #  Maximum delay between roll call bursts.

        # Predefined values for the fireworks show:
        duration_s = 10
        min_delay_ms = 50
        max_delay_ms = 300
        fade_duration_ms = 100
        fade_steps = 10

        # Inner function to simulate a firework burst:
        def do_firework_burst(index, color):
            fade_delay = fade_duration_ms // fade_steps
            r, g, b = color
            for i in range(fade_steps):
                fade_factor = (fade_steps - i) / fade_steps
                self.np_light.set_color(
                    index,
                    (int(r * fade_factor), int(g * fade_factor), int(b * fade_factor)),
                )
                time.sleep_ms(fade_delay)
            self.do_all_off()

        end_time = time.ticks_ms() + duration_s * 1000
        groups = [
            ([0, 1], (87, 8, 255)),  # Group 1 (Purple) for NeoPixels 1 and 2.
            ([2, 3], (255, 0, 255)),  # Group 2 (Magenta) for NeoPixels 3 and 4.
            ([4, 5, 6], (0, 100, 100)),  # Group 3 (Cyan) for NeoPixels 5, 6, and 7.
        ]

        while time.ticks_ms() < end_time:
            # Randomly select a group:
            group_indices, group_color = random.choice(groups)

            # Simulate a roll call burst for the LEDs in the chosen group:
            for index in group_indices:
                do_firework_burst(index, group_color)

            # Delay for a random duration before the next burst:
            time.sleep_ms(random.randint(min_delay_ms, max_delay_ms))

    def do_warm_swell(self):
        """
        Creates a warm swell effect, where LEDs gradually brighten and then
        fade.
        """

        # Predefined duration, color and steps:
        duration_s = 5  # Total duration of the swell effect in seconds.
        swell_color = (255, 100, 0)  #  Color tuple (R, G, B) for the swell.
        swell_steps = (
            100  # Number of steps for the swell to reach max brightness and fade.
        )

        delay_time = duration_s / (2 * swell_steps)  # Adjusted for up and down

        # Swell up and down:
        for step in range(2 * swell_steps):
            # Using a sine function for smoother transitions:
            ratio = (math.sin(math.pi * step / swell_steps) + 1) / 2
            color = (
                int(swell_color[0] * ratio),
                int(swell_color[1] * ratio),
                int(swell_color[2] * ratio),
            )
            for i in range(7):
                self.np_light.set_color(i, color)
            time.sleep_ms(int(delay_time * 1000))

        # Turn off the LEDs at the end:
        self.do_all_off()

    def do_predator_countdown(self):
        """
        Simulates the countdown timer effect from the movie Predator.
        """

        # Predefined duration:
        duration_s = 10  # Total duration of the countdown effect in seconds.

        # Groupings for the LEDs: First 2, next 2, last 3.
        groups = [[0, 1], [2, 3], [4, 5, 6]]

        # Each group will have an equal share of the total duration:
        delay_per_group = duration_s / len(groups)

        dim_red = (50, 0, 0)  # Dim red color for LEDs that are about to turn off.
        bright_red = (255, 0, 0)  # Bright red color for active LEDs.

        # Initialize all LEDs to bright red:
        self.np_light.fill(bright_red)

        # Iterate through the LED groups:
        for group in groups:
            # Blink the current group LEDs back and forth for a bit:
            end_time_group = time.ticks_ms() + delay_per_group * 1000
            while time.ticks_ms() < end_time_group:
                # Alternate a limited number of times (3 in this case):
                for _ in range(3):
                    for led in group:
                        self.np_light.set_color(led, dim_red)
                        time.sleep_ms(500)
                        self.np_light.set_color(led, bright_red)
                        time.sleep_ms(500)

                # For the last group of 3 LEDs, turn them off one at a time:
                if group == [4, 5, 6]:
                    for led in reversed(group):
                        self.np_light.set_color(led, (0, 0, 0))
                        time.sleep_ms(500)
                # For the other groups, turn off the LEDs in order:
                else:
                    for led in group:
                        self.np_light.set_color(led, (0, 0, 0))
                        time.sleep_ms(500)

    def do_predator_purple_magenta_cyan_countdown(self):
        """
        Simulates the cyan-magenta-purple countdown timer effect similar to
        the movie Predator.
        """

        # Groupings for the LEDs: First 2, next 2, last 3:
        groups = [[0, 1], [2, 3], [4, 5, 6]]

        # Purple, Magenta, Cyan colors for the countdown:
        colors = [(87, 8, 255), (255, 0, 255), (0, 100, 100)]

        # Bright white color for LEDs:
        white = (255, 255, 255)

        # Dim white color for LEDs that have been counted down:
        dim_white = (50, 50, 50)

        # Initialize all LEDs to bright white:
        self.np_light.fill(white)

        # Increase the number of cycles to make the patterns more noticeable:
        cycles_per_group = 5

        # Iterate through the LED groups:
        for group in groups:
            for _ in range(cycles_per_group):
                for current_color in colors:
                    for led in group:
                        self.np_light.set_color(led, current_color)
                        time.sleep_ms(200)  # Quick alternation for a fast cycle.
                        self.np_light.set_color(led, dim_white)
                        time.sleep_ms(200)

            # For the last group of 3 LEDs, turn them off one at a time:
            if group == [4, 5, 6]:
                for led in reversed(group):
                    self.np_light.set_color(led, (0, 0, 0))
                    time.sleep_ms(500)
            # For the other groups, turn off the LEDs in order:
            else:
                for led in group:
                    self.np_light.set_color(led, (0, 0, 0))
                    time.sleep_ms(500)

    def do_slot_machine_effect(self):
        """
        Simulates the vibrant blinking effect similar to a slot machine.
        """

        # Predefined duration:
        duration_s = 10  # Total duration of the slot machine effect in seconds.

        # Define some vibrant colors: Red, Green, Blue, Yellow, Cyan, Magenta,
        # White:
        vibrant_colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (0, 100, 100),
            (255, 0, 255),
            (87, 8, 255),
        ]

        end_time = time.ticks_ms() + duration_s * 1000

        # Main loop for the duration of the effect:
        while time.ticks_ms() < end_time:
            # Randomly choose a vibrant color:
            chosen_color = random.choice(vibrant_colors)

            # Sequentially light up each LED with the chosen color:
            for led in range(7):
                self.np_light.set_color(led, chosen_color)
                time.sleep_ms(100)  # Brief delay for the 'motion' effect.
                self.np_light.set_color(led, (0, 0, 0))  # Turn off the LED.

            # After completing a sequence, let's add a rapid blinking effect:
            for _ in range(3):  # 3 times for a noticeable effect.
                self.np_light.fill(chosen_color)
                time.sleep_ms(100)  # ON state delay.
                self.do_all_off()
                time.sleep_ms(100)  # OFF state delay.

    def do_jackpot_effect(self):
        """
        Simulates a jackpot effect similar to a slot machine hitting a big win.
        """

        # Predefined duration:
        duration_s = 10  # Total duration of the jackpot effect in seconds.

        # Define some vibrant colors: Red, Green, Blue, Yellow, Cyan, Magenta,
        # White:
        vibrant_colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (0, 100, 100),
            (255, 0, 255),
            (87, 8, 255),
        ]

        # 1. Fast Blinking:
        for _ in range(5):
            self.do_all_off()
            time.sleep_ms(50)
            self.np_light.fill(random.choice(vibrant_colors))
            time.sleep_ms(50)

        # 2. Wave of Colors:
        for color in vibrant_colors:
            for led in range(7):
                self.np_light.set_color(led, color)
                time.sleep_ms(100)
                self.np_light.set_color(led, (0, 0, 0))

        # 3. Random Pulsing:
        pulse_end_time = time.ticks_ms() + 2 * 1000  # Pulse for 2 seconds.
        while time.ticks_ms() < pulse_end_time:
            led = random.randint(0, 6)
            self.np_light.set_color(led, random.choice(vibrant_colors))
            time.sleep_ms(100)
            self.np_light.set_color(led, (0, 0, 0))
            time.sleep_ms(50)

        # 4. Prolonged Brightness:
        self.np_light.fill((87, 8, 255))
        time.sleep_ms(duration_s * 1000 - (pulse_end_time - time.ticks_ms()))

        # Turn off the LEDs at the end:
        self.do_all_off()

    def do_boot_sequence(self):
        """
        Simulates a boot sequence with a warm swell effect followed by rapid blinking.
        Each group of LEDs will swell from off to full brightness and back, then blink.
        The first two groups stay on in a dimmed state, and the third group pauses at the dim level before turning off.
        """

        groups = [[0, 1], [2, 3], [4, 5, 6]]
        # Purple, Magenta, Cyan:
        colors = [(87, 8, 255), (255, 0, 255), (0, 100, 100)]
        swell_steps = 20  # Number of steps for swelling up and down.
        blink_count = 2  # Number of blinks.
        post_swell_delay = 1337  # Time in ms to wait after the last swell.

        # Function for a warm swell effect
        def swell(group, color, final_intensity=1.0):
            # Swell up
            for step in range(swell_steps):
                intensity = step / swell_steps
                adjusted_color = (
                    int(color[0] * intensity),
                    int(color[1] * intensity),
                    int(color[2] * intensity),
                )
                for led in group:
                    self.np_light.set_color(led, adjusted_color)
                time.sleep_ms(50)

            # Swell down
            for step in range(swell_steps, 0, -1):
                intensity = step / swell_steps
                adjusted_color = (
                    int(color[0] * intensity),
                    int(color[1] * intensity),
                    int(color[2] * intensity),
                )
                for led in group:
                    self.np_light.set_color(led, adjusted_color)
                time.sleep_ms(50)

            # Set to final intensity
            dim_color = (
                int(color[0] * final_intensity),
                int(color[1] * final_intensity),
                int(color[2] * final_intensity),
            )
            for led in group:
                self.np_light.set_color(led, dim_color)

        # Function for blinking
        def blink(group, color):
            for _ in range(blink_count):
                for led in group:
                    self.np_light.set_color(led, color)  # On.
                time.sleep_ms(100)
                for led in group:
                    self.np_light.set_color(led, (0, 0, 0))  # Off.
                time.sleep_ms(100)

        # Perform the sequence for each group
        for index, (group, color) in enumerate(zip(groups, colors)):
            swell(group, color)  # Warm swell effect.
            blink(group, color)  # Blinking effect.
            swell(
                group, color, final_intensity=0.2
            )  # Warm swell effect again with dimming.

            # For the last group, pause at the dim level before turning off:
            if index == len(groups) - 1:
                time.sleep_ms(post_swell_delay)

        # Ensure all LEDs are turned off at the end:
        self.do_all_off()
