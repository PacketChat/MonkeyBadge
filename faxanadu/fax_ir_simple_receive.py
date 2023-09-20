import machine
from machine import Pin
import utime
import neopixel


# Define the GPIO pin for IR receiver:
IR_RECEIVER_PIN = 19

# Initialize the GPIO pin for IR receiver:
ir_receiver = Pin(IR_RECEIVER_PIN, Pin.IN)

# Number of NeoPixels:
NUM_PIXELS = 7

# Utility Function:
def scale_color(rgb, brightness_factor):
    """
    Scales an RGB color tuple based on the provided brightness factor.

    Parameters:
    :param rgb: Tuple of (R, G, B) values.
    :param brightness_factor: A float between 0 (off) and 1 (full brightness).
    :return: Scaled RGB tuple.
    """
    return tuple(int(val * brightness_factor) for val in rgb)

# Class for the NeoPixel:
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

# Function to capture an IR signal and return the pulse durations:
def capture_ir_signal():
    signal = []
    while True:
        # Wait for the start of an IR signal (rising edge):
        while ir_receiver.value() == 0:
            pass
        pulse_start_time = utime.ticks_us()

        # Wait for the end of the IR signal (falling edge):
        while ir_receiver.value() == 1:
            pass
        pulse_duration = utime.ticks_us() - pulse_start_time

        # Store the pulse duration in the signal:
        signal.append(pulse_duration)

        # Check for the end of the signal (e.g., a long gap):
        if pulse_duration > 20000:  # Adjust the gap threshold as needed.
            return signal

# Function to decode a phase-encoded signal:
def decode_phase_encoded_signal(signal):
    decoded_signal = []
    for duration in signal:
        if duration > 800:  # Threshold for +1000.
            decoded_signal.append(+1000)
        else:  # Threshold for -500.
            decoded_signal.append(-500)
    return decoded_signal

# Initialize the NeoPixels:
neopixel = NeoPixelLight(18, 7, brightness=0.025)

# Capture and decode the IR signal:
while True:
    print("Waiting for an IR signal...")
    captured_signal = capture_ir_signal()
    decoded_signal = decode_phase_encoded_signal(captured_signal)
    # Debugging:
    print("Received Signal:", decoded_signal)
    if decoded_signal[0] == 1000:
        # Set NeoPixels to red:
        for i in range(NUM_PIXELS):
            neopixel.set_color(i, (0, 180, 180))

