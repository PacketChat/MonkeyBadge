import machine, neopixel, time, network
from machine import Pin, I2C
import ssd1306
np = neopixel.NeoPixel(machine.Pin(18), 7)
slval = 50

#Addressable LED Test
def do_all_off():
    for i in range(7):
      np[i] = (0, 0, 0)
      np.write()


def do_canz_spaz():
   np[2] = (0, 0, 0)
   np[3] = (0, 0, 0)   
   for i in range(255):
     np[2] = (25, 32, i)
     np[3] = (i, 55, 32)
     #time.sleep_ms(50)
     np.write()
   np[2] = (0, 0, 0)
   np[3] = (0, 0, 0) 
   np.write()   

do_canz_spaz()

#def do_cans_spaz():

#def do_mic_spaz():

def do_greensweep():
     for i in range(7):
       np[i] = (0, 0, 0)
       np.write()
       time.sleep_ms(slval)
     for i in range(7):
       np[i] = (0, 32, 0)
       np.write()
       time.sleep_ms(slval)

do_greensweep()
do_all_off()

def do_redsweep():
     for i in range(7):
       np[i] = (0, 0, 0)
       np.write()
       time.sleep_ms(slval)
     for i in range(7):
       np[i] = (32, 0, 0)
       np.write()
       time.sleep_ms(slval)

do_redsweep()
do_all_off()

def do_bluesweep():
     for i in range(7):
       np[i] = (0, 0, 0)
       np.write()
       time.sleep_ms(slval)
     for i in range(7):
       np[i] = (0, 0, 32)
       np.write()
       time.sleep_ms(slval)

do_bluesweep()
do_all_off()


def do_purplesweep():
     for i in range(7):
       np[i] = (0, 0, 0)
       np.write()
       time.sleep_ms(slval)
     for i in range(7):
       np[i] = (32, 0, 32)
       np.write()
       time.sleep_ms(slval)

do_purplesweep()
do_all_off()
