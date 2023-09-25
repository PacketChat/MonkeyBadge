import machine
import utime

# Define GPIO pins for IR LED
IR_LED_PIN = 17

# Set the carrier frequency to 38 kHz
carrier_frequency = 38000

# Set the duty cycle (about 33%)
duty_cycle = 360

# Create PWM object for IR LED
ir_pwm = machine.PWM(machine.Pin(IR_LED_PIN), freq=carrier_frequency, duty=duty_cycle)

# Function to send a single pulse
def send_pulse(on_duration_us, off_duration_us):
    ir_pwm.duty(duty_cycle)  # Turn on the IR LED (33% duty cycle)
    utime.sleep_us(on_duration_us)
    ir_pwm.duty(0)   # Turn off the IR LED
    utime.sleep_us(off_duration_us)

# Function to send an IR frame
def send_ir_frame(data):
    # Send the initial start byte
    send_pulse(9000, 4500)  # Long pulse (on) followed by long off time

    # Send each bit in the data
    for bit in data:
        if bit == 1:
            send_pulse(560, 560)  # Short pulse for 1 with longer silence
            #send_pulse(560, 1120)
        else:
            send_pulse(560, 280)  # Short pulse for 0 with shorter silence
            #send_pulse(560, 560)

if __name__ == "__main__":
    while True:
        # Define the data to be sent (e.g., [1, 0, 1, 1, 0, 0, 1, 0])
        #data_to_send = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0]
        data_to_send = [1]
        #data_to_send = [0]
        #data_to_send = [1, 1, 1, 1]
        #data_to_send = [0, 0, 0, 0]


        # Send an IR frame with the specified data
        send_ir_frame(data_to_send)

        utime.sleep(2)  # Wait for 2 seconds before sending the next frame

