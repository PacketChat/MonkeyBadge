from machine import ADC
from machine import Pin, I2C
import ssd1306

Potentiometer = ADC(Pin(36)) #GPIO Pin 26 defined for input
#Potentiometer.atten(ADC.ATTN_11DB)  #TODO: This is for 3.3V, need better value

def mic_pressed(pin):
    print('mic button pressed')
    i2c = I2C(sda=Pin(5), scl=Pin(23))
    display = ssd1306.SSD1306_I2C(128, 64, i2c)
    display.fill(0) # set everything to black
    display.show() # Activate
    p_mic = Pin(13, Pin.IN, Pin.PULL_UP)
    p_mic.irq(handler=mic_pressed, trigger=Pin.IRQ_FALLING)
    Potentiometer_val = Potentiometer.read()
    display.text(f'BatLevel: {Potentiometer_val}', 0, 0, 1)
    display.show() # Activate with new parameters

