import machine
import utime

# Define the GPIO pin connected to the output of the IR receiver
IR_RECEIVER_PIN = 19

# Tolerances for the timings
TOLERANCE = 150

# Define pulse and space timings
PREAMBLE_PULSE = 9000
PREAMBLE_SPACE = 4500
ONE_PULSE = 560
ONE_SPACE = 560
ZERO_PULSE = 560
ZERO_SPACE = 280

# Initialize the pin
ir_receiver = machine.Pin(IR_RECEIVER_PIN, machine.Pin.IN)

def measure_pulse():
    """
    Measure the duration of a pulse (time the signal is low)
    Returns the duration of the pulse in microseconds.
    """
    start_time = utime.ticks_us()
    while ir_receiver.value() == 0:
        pass
    end_time = utime.ticks_us()
    return utime.ticks_diff(end_time, start_time)

def measure_space():
    """
    Measure the duration of space (time the signal is high)
    Returns the duration of the space in microseconds.
    """
    start_time = utime.ticks_us()
    while ir_receiver.value() == 1:
        pass
    end_time = utime.ticks_us()
    return utime.ticks_diff(end_time, start_time)

def is_approximate(value, target, tolerance=TOLERANCE):
    """
    Check if the value is within the range defined by tolerance.
    Returns True if the value is within the tolerance range, False otherwise.
    """
    return target - tolerance <= value <= target + tolerance

def decode_ir():
    """
    Decode the IR signal and return the decoded data as a list of bits (0s and
    1s). Returns None if the signal cannot be decoded.
    """
    data = []

    # Check for preamble
    if not (is_approximate(measure_pulse(), PREAMBLE_PULSE) and is_approximate(measure_space(), PREAMBLE_SPACE)):
        return None

    # Wait for the end of preamble
    while not is_approximate(measure_space(), PREAMBLE_SPACE):
        pass

    # Read the subsequent data bits
    while True:
        pulse_duration = measure_pulse()
        space_duration = measure_space()

        # Decode a '1'
        if (is_approximate(pulse_duration, ONE_PULSE) and
            is_approximate(space_duration, ONE_SPACE)):
            data.append(1)
        # Decode a '0'
        elif (is_approximate(pulse_duration, ZERO_PULSE) and
              is_approximate(space_duration, ZERO_SPACE)):
            data.append(0)
        else:
            # End of data or unrecognized pattern
            break

    return data

if __name__ == "__main__":
    while True:
        if ir_receiver.value() == 0:  # If a pulse is detected
            decoded_data = decode_ir()
            if decoded_data is not None:
                print(decoded_data)
            # Short pause to avoid re-triggering on the same signal
            utime.sleep_ms(10)

