import machine
import utime

# Define GPIO pins for IR LED:
IR_LED_PIN = 17

# Set the carrier frequency to 38 kHz:
CARRIER_FREQUENCY = 38000

# Set the duty cycle (about 33%):
DUTY_CYCLE = 360

# Define pulse and space timings:
PREAMBLE_PULSE = 9000
PREAMBLE_SPACE = 4500
ONE_PULSE = 560
ONE_SPACE = 560
ZERO_PULSE = 560
ZERO_SPACE = 280
END_PULSE = 2750
END_SPACE = 2750

# Create PWM object for IR LED:
ir_pwm = machine.PWM(machine.Pin(IR_LED_PIN), freq=CARRIER_FREQUENCY, duty=DUTY_CYCLE)

# Function to send a single pulse:
def send_pulse(on_duration_us, off_duration_us):
    """
    Send a single pulse with the specified on and off durations.

    Args:
        on_duration_us (int): Duration of the pulse in microseconds.
        off_duration_us (int): Duration of the silence in microseconds.
    """
    ir_pwm.duty(DUTY_CYCLE)         # Turn on the IR LED (33% duty cycle).
    utime.sleep_us(on_duration_us)
    ir_pwm.duty(0)                  # Turn off the IR LED.
    utime.sleep_us(off_duration_us)

# Function to send an IR frame:
def send_ir_frame(data):
    """
    Send an IR frame with the specified data.

    Args:
        data (list): List of bits (0 or 1) to be transmitted.
    """
    # Long pulse (on) followed by long off time:
    send_pulse(PREAMBLE_PULSE, PREAMBLE_SPACE)

    # Send each bit in the data:
    for bit in data:
        if bit == 1:
            send_pulse(ONE_PULSE, ONE_SPACE)  # Short pulse for 1 with longer silence.
        else:
            send_pulse(ZERO_PULSE, ZERO_SPACE)  # Short pulse for 0 with shorter silence.

    # Send the medium ending pulse:
    send_pulse(END_PULSE, END_SPACE)

if __name__ == "__main__":
    while True:
        # Define the data to be sent (e.g., [0, 0, 1, 1, 0, 0, 0, 1]):

        # Test 4 bits:
        #data_to_send = [1, 1, 1, 1]

        # Test 8 bits:
        #data_to_send = [0, 0, 1, 1, 0, 0, 0, 1]

        # Test 64 bits:
        data_to_send = [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1]

        # Send an IR frame with the specified data:
        send_ir_frame(data_to_send)

        utime.sleep(1)  # Wait for 2 seconds before sending the next frame.

