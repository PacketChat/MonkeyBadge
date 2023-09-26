from machine import Pin, PWM
import utime

# Define the GPIO pin for IR transmitter:
IR_TRANSMITTER_PIN = 17

# Initialize the GPIO pin for IR transmitter:
ir_transmitter = PWM(Pin(IR_TRANSMITTER_PIN))

# Set the carrier frequency (38kHz for NEC protocol, adjust if needed):
CARRIER_FREQUENCY = 38000

# Configure the PWM frequency and duty cycle:
ir_transmitter.freq(CARRIER_FREQUENCY)
ir_transmitter.duty(360)  # ~33% duty cycle (Values: 0-1023).

# Function to send a phase-encoded signal:
def send_phase_encoded_signal(signal):
    for duration in signal:
        send_ir_pulse(duration)

# Function to send an IR pulse with a specific duration in microseconds:
def send_ir_pulse(duration_us):
    ir_transmitter.duty(512)  # Turn on the IR LED.
    # Sleep for the absolute value of the duration.
    utime.sleep_us(abs(duration_us))
    ir_transmitter.duty(0)    # Turn off the IR LED.

# Phase-encoded signal as provided:
signal = [-500, 500, -500, 1000, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -1000, 500]

# Send the phase-encoded signal:
send_phase_encoded_signal(signal)

