"""
IR Message Sender

This program sends an ASCII message using binary signals using an IR LED.

GPIO Pin Configuration:
- IR LED is connected to GPIO pin 17.

IR Signal Details:
- Carrier Frequency: 38 kHz
- Duty Cycle: 33%

Signal Timings:
- Preamble: 9000 µs ON, 4500 µs OFF
- Bit 1: 560 µs ON, 560 µs OFF
- Bit 0: 560 µs ON, 280 µs OFF
- End Pulse: 2750 µs ON (used for ending the signal)

Usage:
- Define the ASCII message to be sent.
- The message is converted to binary representation.
- The binary message is sent as an IR frame.

"""

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

def send_ir_frame(data):
    """
    Send an IR frame with the specified data.

    Args:
        data (str): Binary representation of the message to be sent.
    """
    # Long pulse (on) followed by long off time:
    send_pulse(PREAMBLE_PULSE, PREAMBLE_SPACE)

    # Send each bit in the data:
    for bit in data:
        if bit == '1':
            send_pulse(ONE_PULSE, ONE_SPACE)  # Short pulse for 1 with longer silence.
        else:
            send_pulse(ZERO_PULSE, ZERO_SPACE)  # Short pulse for 0 with shorter silence.

    # Send the medium ending pulse:
    send_pulse(END_PULSE, END_SPACE)

def ascii_to_binary(message):
    """
    Convert ASCII characters to binary representation.
    """
    binary_message = ''
    for char in message:
        binary_char = '{:08b}'.format(ord(char))
        binary_message += binary_char
    return binary_message

if __name__ == "__main__":
    while True:
        # Define the ASCII message to be sent:
        ascii_message = "Hack the planet!"

        # Convert the ASCII message to a binary representation of the message:
        binary_message = ascii_to_binary(ascii_message)

        # Send an IR frame with the binary representation of the message:
        send_ir_frame(binary_message)

        utime.sleep(5)  # Wait for 5 seconds before sending the next frame.

