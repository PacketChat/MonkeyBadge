#Basic Badge Tests
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

       
def do_kanzwink():
    print ('Kanz has an evil left eye.  Did it wink at you?')
    import machine
    evileye = Pin(2, Pin.OUT)
    evileye.value(1)
    time.sleep_ms(slval)
    evileye.value(0)
    time.sleep_ms(slval)
    evileye.value(1)
    time.sleep_ms(slval)
    evileye.value(0)

do_bluesweep()
do_redsweep()
do_purplesweep()
do_greensweep()
do_kanzwink()
do_all_off()


# Evil Eye Tests
print ('Kanz has an evil left eye.  Did it wink at you?')
import machine
evileye = Pin(2, Pin.OUT)
evileye.value(1)
time.sleep_ms(slval)
evileye.value(0)
time.sleep_ms(slval)
evileye.value(1)
time.sleep_ms(slval)
evileye.value(0)


#Wifi Tests
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    do_redsweep()
    wlan.connect('WillHouse6', 'williams123')
    while not wlan.isconnected():
      pass

do_greensweep()
print('network config', wlan.ifconfig())
do_all_off()

#TODO: Add WebREPL 
#TODO: Create some kind of P2P socket interactive game
#ala second Ninja Badge Kung Fu 

#Buttons
#Button GPIO's are as follows:  UP=4, DN=14, CANZ=15, mic=13
from machine import Pin
def up_pressed(pin):
   print('up button pressed')
   do_greensweep()
   do_all_off()

def dn_pressed(pin):
   print('down button pressed')
   do_redsweep()
   do_all_off()

def canz_pressed(pin):
   print('canz button pressed')
   do_bluesweep()
   do_all_off()

def mic_pressed(pin):
   print('mic button pressed')
   do_purplesweep()
   do_all_off()

p_up = Pin(4, Pin.IN, Pin.PULL_UP)
p_dn = Pin(14, Pin.IN, Pin.PULL_UP)
p_canz = Pin(15, Pin.IN, Pin.PULL_UP)
p_mic = Pin(13, Pin.IN, Pin.PULL_UP)

p_up.irq(handler=up_pressed, trigger=Pin.IRQ_FALLING)
p_dn.irq(handler=dn_pressed, trigger=Pin.IRQ_FALLING)
p_canz.irq(handler=canz_pressed, trigger=Pin.IRQ_FALLING)
p_mic.irq(handler=mic_pressed, trigger=Pin.IRQ_FALLING)

print('Buttons loaded.  Please press each button one at a time to test.')


#OLED
print('Loading OLED display driver.  If it works, you should see Hushcon-Seattle 2023 on the OLED screen.')

from machine import Pin, I2C
import ssd1306
i2c = I2C(sda=Pin(5), scl=Pin(23))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
display.fill(0) # set everything to black
display.show() # Activate
display.text('Hushcon-Seattle', 0, 0, 1)
display.text('2023', 45, 15, 1) # draw some text at x=0, y=0, color=1
display.show() # Activate with new parameters


#Create Filesystem
#I don't think this works yet, but it doesn't crash.

class RAMBlockDev:
    def __init__(self, block_size, num_blocks):
        self.block_size = block_size
        self.data = bytearray(block_size * num_blocks)

    def readblocks(self, block_num, buf):
        for i in range(len(buf)):
            buf[i] = self.data[block_num * self.block_size + i]

    def writeblocks(self, block_num, buf):
        for i in range(len(buf)):
            self.data[block_num * self.block_size + i] = buf[i]

    def ioctl(self, op, arg):
        if op == 4: # get number of blocks
            return len(self.data) // self.block_size
        if op == 5: # get block size
            return self.block_size

import os

bdev = RAMBlockDev(512, 50)
os.VfsFat.mkfs(bdev)
os.mount(bdev, '/ramdisk')

#FM Receiver & Audio Amp
#import si470x
#rd=si470x.SI470X()
#rd.tunFreq(90.9)
#rd.setVolume(12)
#rd.getStatus()
print('Until I figure out how to upload the si470x library, leave above code commented.  Cant test FM Receiver chip, skipping...')

#Possible libraries:
#https://pypi.org/project/ucdev/
#https://github.com/ryedwards/si4703RaspberryPi
# si4702 control via i2c





