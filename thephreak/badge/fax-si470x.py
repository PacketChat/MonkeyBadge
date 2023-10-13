# MicroPython's constant module for memory-efficient constants:
from micropython import const
# For memory-mapped struct-like objects:
from uctypes import struct, addressof
# For struct manipulation:
from uctypes import BF_POS, BF_LEN, UINT16, BFUINT16, BIG_ENDIAN
import time
import machine
# Note: I'm using SoftI2C because while importing I2C we got a deprecation
# warning:
from machine import Pin, SoftI2C
import ssd1306

# Constants:

# Define available bands and channel spacing options:
BAND_US = const(0)          # United States band.
BAND_JP_WIDE = const(1)     # Japan wide band.
BAND_JP = const(2)          # Japan band.
CSPACE_US = const(0)        # Channel spacing for the United States.
CSPACE_WORLD = const(1)     # Channel spacing for the rest of the world.
CSPACE_NARROW = const(2)    # Narrow channel spacing.

DEVICEID_FIELDS = {
    # Register 0x00 - DEVICEID
    "PN": 12 << BF_POS | 4 << BF_LEN | BFUINT16,
    "MFGID": 0 << BF_POS | 12 << BF_LEN | BFUINT16,
}

CHIPID_FIELDS = {
    # Register 0x01 - CHIPID
    "REV": 10 << BF_POS | 6 << BF_LEN | BFUINT16,
    "DEV": 6 << BF_POS | 4 << BF_LEN | BFUINT16,
    "FIRMWARE": 0 << BF_POS | 6 << BF_LEN | BFUINT16,
}

POWERCFG_FIELDS = {
    # Register 0x02 - POWERCFG
    "DSMUTE": 15 << BF_POS | 1 << BF_LEN | BFUINT16,
    "DMUTE": 14 << BF_POS | 1 << BF_LEN | BFUINT16,
    "MONO": 13 << BF_POS | 1 << BF_LEN | BFUINT16,
    "RDSM": 11 << BF_POS | 1 << BF_LEN | BFUINT16,
    "SKMODE": 10 << BF_POS | 1 << BF_LEN | BFUINT16,
    "SEEKUP": 9 << BF_POS | 1 << BF_LEN | BFUINT16,
    "SEEK": 8 << BF_POS | 1 << BF_LEN | BFUINT16,
    "DISABLE": 6 << BF_POS | 1 << BF_LEN | BFUINT16,
    "ENABLE": 0 << BF_POS | 1 << BF_LEN | BFUINT16,
}

CHANNEL_FIELDS = {
    # Register 0x03 - CHANNEL
    "TUNE": 15 << BF_POS | 1 << BF_LEN | BFUINT16,
    "CHAN": 0 << BF_POS | 10 << BF_LEN | BFUINT16,
}

SYSCONFIG1_FIELDS = {
    # Register 0x04 - SYSCONFIG1
    "RDSIEN": 15 << BF_POS | 1 << BF_LEN | BFUINT16,
    "STCIEN": 14 << BF_POS | 1 << BF_LEN | BFUINT16,
    "RDS": 12 << BF_POS | 1 << BF_LEN | BFUINT16,
    "DE": 11 << BF_POS | 1 << BF_LEN | BFUINT16,
    "AGCD": 10 << BF_POS | 1 << BF_LEN | BFUINT16,
    "BLNDADJ": 6 << BF_POS | 2 << BF_LEN | BFUINT16,
    "GPIO3": 4 << BF_POS | 2 << BF_LEN | BFUINT16,
    "GPIO2": 2 << BF_POS | 2 << BF_LEN | BFUINT16,
    "GPIO1": 0 << BF_POS | 2 << BF_LEN | BFUINT16,
}

SYSCONFIG2_FIELDS = {
    # Register 0x05 - SYSCONFIG2
    "SEEKTH": 8 << BF_POS | 8 << BF_LEN | BFUINT16,
    "BAND": 6 << BF_POS | 2 << BF_LEN | BFUINT16,
    "SPACE": 4 << BF_POS | 2 << BF_LEN | BFUINT16,
    "VOLUME": 0 << BF_POS | 4 << BF_LEN | BFUINT16,
}

SYSCONFIG3_FIELDS = {
    # Register 0x06 - SYSCONFIG3
    "SMUTER": 14 << BF_POS | 2 << BF_LEN | BFUINT16,
    "SMUTEA": 12 << BF_POS | 2 << BF_LEN | BFUINT16,
    "VOLEXT": 8 << BF_POS | 1 << BF_LEN | BFUINT16,
    "SKSNR": 4 << BF_POS | 4 << BF_LEN | BFUINT16,
    "SKCNT": 0 << BF_POS | 4 << BF_LEN | BFUINT16,
}

TEST1_FIELDS = {
    # Register 0x07 - TEST1
    "XOSCEN": 15 << BF_POS | 1 << BF_LEN | BFUINT16,
    "AHIZEN": 14 << BF_POS | 1 << BF_LEN | BFUINT16,
}

STATUSRSSI_FIELDS = {
    # Register 0x0A - STATUSRSSI
    "RDSR": 15 << BF_POS | 1 << BF_LEN | BFUINT16,
    "STC": 14 << BF_POS | 1 << BF_LEN | BFUINT16,
    "SFBL": 13 << BF_POS | 1 << BF_LEN | BFUINT16,
    "AFCRL": 12 << BF_POS | 1 << BF_LEN | BFUINT16,
    "RDSS": 11 << BF_POS | 1 << BF_LEN | BFUINT16,
    "BLERA": 9 << BF_POS | 2 << BF_LEN | BFUINT16,
    "ST": 8 << BF_POS | 1 << BF_LEN | BFUINT16,
    "RSSI": 0 << BF_POS | 8 << BF_LEN | BFUINT16,
}

READCHAN_FIELDS = {
    # Register 0x0B - READCHAN
    "BLERB": 14 << BF_POS | 2 << BF_LEN | BFUINT16,
    "BLERC": 12 << BF_POS | 2 << BF_LEN | BFUINT16,
    "BLERD": 10 << BF_POS | 2 << BF_LEN | BFUINT16,
    "READCHAN": 0 << BF_POS | 10 << BF_LEN | BFUINT16,
}

SI470X_REGS = {
    # The astute observer will notice that these values don't match up with the
    # register map in datasheet.  That's because when reading data all reads
    # will ***always*** begin at address 0x0A.  Effectively, just imagine the
    # response always being delivered on magnetic tape and there being no
    # "seek" mechanism.
    "STATUSRSSI_REG": 0x00 | UINT16,
    "STATUSRSSI": (0x00, STATUSRSSI_FIELDS),
    "READCHAN_REG": 0x02 | UINT16,
    "READCHAN": (0x02, READCHAN_FIELDS),
    "RDSA_REG": 0x04 | UINT16,
    "RDSB_REG": 0x06 | UINT16,
    "RDSC_REG": 0x08 | UINT16,
    "RDSD_REG": 0x0A | UINT16,
    "DEVICEID_REG": 0x0C | UINT16,
    "DEVICEID": (0x0C, DEVICEID_FIELDS),
    "CHIPID_REG": 0x0E | UINT16,
    "CHIPID": (0x0E, CHIPID_FIELDS),
    "POWERCFG_REG": 0x10 | UINT16,
    "POWERCFG": (0x10, POWERCFG_FIELDS),
    "CHANNEL_REG": 0x12 | UINT16,
    "CHANNEL": (0x12, CHANNEL_FIELDS),
    "SYSCONFIG1_REG": 0x14 | UINT16,
    "SYSCONFIG1": (0x14, SYSCONFIG1_FIELDS),
    "SYSCONFIG2_REG": 0x16 | UINT16,
    "SYSCONFIG2": (0x16, SYSCONFIG2_FIELDS),
    "SYSCONFIG3_REG": 0x18 | UINT16,
    "SYSCONFIG3": (0x18, SYSCONFIG3_FIELDS),
    "TEST1_REG": 0x1A | UINT16,
    "TEST1": (0x1A, TEST1_FIELDS),
    "TEST2_REG": 0x1C | UINT16,
    "BOOTCONFIG_REG": 0x1E | UINT16,
}

# Classes:
class Button:
    """
    A class for initializing buttons and handling button press events with
    debounce logic.
    """

    # The time in milliseconds for button debounce.
    DEBOUNCE_DELAY_MS = 50

    def __init__(self, pin, callback):
        """
        Initialize the button with the given pin and a callback function to
        execute on button press.

        :param pin: The pin connected to the button.
        :param callback: The function to be called when the button is pressed.
        """
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pin.irq(handler=self._pressed, trigger=machine.Pin.IRQ_FALLING)
        self.callback = callback

    def _pressed(self, pin):
        """
        Private method to handle button press with debouncing.

        This method is automatically called when the button is pressed.
        It checks for button debouncing and triggers the callback if the press
        is valid.
        """
        if self.debounce():
            self.callback()
            # Wait for the button to be released before allowing another press:
            while self.pin.value() == 0:
                pass

    def debounce(self):
        """
        Perform button debouncing to ensure a valid button press event.

        This method helps eliminate false positives caused by button bouncing.
        :return: True if the button press is valid, False otherwise.
        """
        initial_state = self.pin.value()
        time.sleep_ms(self.DEBOUNCE_DELAY_MS)
        # Check if the button is still pressed and its state hasn't changed
        # during debounce delay:
        return initial_state == 0 and self.pin.value() == 0

class SSD1306:
    """
    A class for controlling an OLED display using the SSD1306 driver.
    """

    def __init__(self, width, height, sda_pin, scl_pin):
        """
        Initialize the OLED display with the given dimensions and I2C pins.

        :param width: Width of the display in pixels.
        :param height: Height of the display in pixels.
        :param sda_pin: The SDA pin for I2C communication.
        :param scl_pin: The SCL pin for I2C communication.
        """
        self.i2c = SoftI2C(sda=Pin(sda_pin), scl=Pin(scl_pin))
        self.display = ssd1306.SSD1306_I2C(width, height, self.i2c)

    def clear(self):
        """
        Clear the display by filling it with black pixels and updating the
        display.
        """
        self.display.fill(0)
        self.display.show()

    def show_text(self, line1='', line2='', line3='', line4='', line5='', line6='', line7=''):
        """
        Display text on the OLED display with specific formatting.

        :param line1: Text for line 1.
        :param line2: Text for line 2.
        :param line3: Text for line 3.
        :param line4: Text for line 4.
        :param line5: Text for line 5.
        :param line6: Text for line 6.

        This method is set up to display text on 7 different lines with 11
        units of height per line.
        """
        self.clear()
        self.display.text(line1, 0, 0, 1)
        self.display.text(line2, 0, 11, 1)
        self.display.text(line3, 0, 22, 1)
        self.display.text(line4, 0, 33, 1)
        self.display.text(line5, 0, 44, 1)
        self.display.text(line6, 0, 55, 1)
        self.display.show()

class SI470X(object):
    def __init__(
        self,
        i2c=None,
        i2c_addr=0x10,
        reset_pin=machine.Pin(16, machine.Pin.OUT),
        tuning=None,
        band=BAND_US,
        channel_space=CSPACE_US,
        rds=False
    ):
        """
        Initialize the SI470X radio object.

        This method initializes the SI470X radio object with the provided
        configuration options.

        Args:
            i2c (machine.I2C, optional): An I2C instance to communicate with
            the SI470X chip. If not provided, a default I2C instance will be
            created.

            i2c_addr (int, optional): The I2C address of the SI470X chip.

            reset_pin (machine.Pin, optional): A Pin instance representing the
            reset pin of the SI470X chip.

            tuning (float, optional): The initial frequency to tune to.

            band (int, optional): The initial radio band to set.

            channel_space (int, optional): The channel spacing to set.

            rds (bool, optional): Whether to enable RDS functionality.

        Note: This method assumes the existence of various methods and
        attributes like `self.reset()`, `self.initialize()`, `self.tune()`,
        `self.setup_buttons()`, and others, which are supposed to be defined
        elsewhere in the class.

        Example usage:
        ```
        radio = SI470X()
        ```
        """
        if i2c is None:
            # If no I2C instance is provided, create a default one:
            i2c = machine.I2C(
                0,
                scl=machine.Pin(22, machine.Pin.OUT),
                sda=machine.Pin(21, machine.Pin.OUT),
            )

        # Initialize instance attributes:
        self.buffer = bytearray(32)  # Create a byte buffer of size 32.
        self.i2c = i2c  # Store the I2C instance for communication.
        self.i2c_addr = i2c_addr  # Store the I2C address of the device.
        self.reset_pin = reset_pin  # Store the reset pin for the device.
        self.band = band  # Store the radio band (e.g., BAND_US).
        self.channel_space = channel_space  # Store the channel spacing (e.g., CSPACE_US).

        # Create a struct to access registers in the buffer:
        self.fields = struct(addressof(self.buffer), SI470X_REGS, BIG_ENDIAN)

        self.volume = 0  # Initialize the volume attribute to 0.

        # Powerup sequence.
        self.reset()
        self.initialize()
        if tuning:
            self.tune(tuning)

        # Register button handlers:
        self.setup_buttons()

    def setup_buttons(self):
        """
        Initialize and set up button handlers for different radio operations.

        This method creates instances of the Button class for controlling
        volume adjustment and frequency seeking. It associates each button
        with a specific callback function that gets executed when the button
        is pressed. The callback functions handle volume adjustments and
        frequency seeking in response to button presses.

        Button-Pin Mapping:
        - volumeUpButton: Button connected to pin 4 for volume increase.
        - volumeDownButton: Button connected to pin 14 for volume decrease.
        - seekUpButton: Button connected to pin 15 for frequency seeking up.
        - seekDownButton: Button connected to pin 13 for frequency seeking down.
        """
        self.volumeUpButton = Button(4, self.volumeUpPressed)
        self.volumeDownButton = Button(14, self.volumeDownPressed)
        self.seekUpButton = Button(15, self.seekUpPressed)
        self.seekDownButton = Button(13, self.seekDownPressed)

    def waitAndFinishTune(self):
        """
        Wait for tuning to complete and finish the tune operation.

        This method waits for the tuning to complete by repeatedly checking the
        STC (Seek/Tune Complete) status bit in the radio's registers. It does
        this in a loop with a countdown, waiting for a specified duration.

        Once tuning is successfully completed, this method finishes the tune
        operation by resetting appropriate flags and updating the registers.

        Note: This method assumes the existence of various methods and
        attributes like `self.getRegs()`, `self.setRegs()`, and others, which
        are supposed to be defined elsewhere in the class.

        Example usage:
        ```
        radio.waitAndFinishTune()
        ```

        Returns:
            None
        """
        c = 100  # Countdown value for waiting.

        while (self.fields.STATUSRSSI.STC == 0) & (c > 0):
            # Continue loop while STC status bit is not set and countdown > 0:
            self.getRegs()
            time.sleep_ms(100)
            c -= 1

        if c < 1:
            print("Countdown expired. Tuning may not have completed.")

        # Resetting flags to finish the tune operation:
        self.fields.POWERCFG.SEEK = 0  # Clear SEEK flag.
        self.fields.CHANNEL.TUNE = 0   # Clear TUNE flag.
        self.setRegs()  # Update the radio's registers.

        c = 100  # Countdown value for waiting after clearing flags:
        while (self.fields.STATUSRSSI.STC != 0) & (c > 1):
            # Wait again for STC to be set after clearing flags:
            self.getRegs()
            time.sleep_ms(100)
            c -= 1

        if c < 1:
            print("Countdown expired. Tuning may not have been finalized.")

    def getStatus(self):
        """
        This is just a little funkiness to try and squeeze most of this onto a
        single screen.  Basically we bind "self.fields" to a shorter variable
        name solely within the scope of the function.
        """

        sf = self.fields
        print(
"   DEVICEID PN      : (0x{:0x}".format(sf.DEVICEID.PN) + f") \t{sf.DEVICEID.PN}\n" +
"   DEVICEID MFGID   : (0x{:0x}".format(sf.DEVICEID.MFGID) + f") \t{sf.DEVICEID.MFGID}\n" +
"     CHIPID REV     : (0x{:0x}".format(sf.CHIPID.REV) + f") \t{sf.CHIPID.REV}\n" +
"     CHIPID DEV     : (0x{:0x}".format(sf.CHIPID.DEV) + f") \t{sf.CHIPID.DEV}\n" +
"     CHIPID FIRMWARE: (0x{:0x}".format(sf.CHIPID.FIRMWARE) + f") \t{sf.CHIPID.FIRMWARE}\n" +
"   POWERCFG DSMUTE  : (0x{:0x}".format(sf.POWERCFG.DSMUTE) + f") \t{sf.POWERCFG.DSMUTE}\n" +
"   POWERCFG DMUTE   : (0x{:0x}".format(sf.POWERCFG.DMUTE) + f") \t{sf.POWERCFG.DMUTE}\n" +
"   POWERCFG MONO    : (0x{:0x}".format(sf.POWERCFG.MONO) + f") \t{sf.POWERCFG.MONO}\n" +
"   POWERCFG RDSM    : (0x{:0x}".format(sf.POWERCFG.RDSM) + f") \t{sf.POWERCFG.RDSM}\n" +
"   POWERCFG SKMODE  : (0x{:0x}".format(sf.POWERCFG.SKMODE) + f") \t{sf.POWERCFG.SKMODE}\n" +
"   POWERCFG SEEKUP  : (0x{:0x}".format(sf.POWERCFG.SEEKUP) + f") \t{sf.POWERCFG.SEEKUP}\n" +
"   POWERCFG SEEK    : (0x{:0x}".format(sf.POWERCFG.SEEK) + f") \t{sf.POWERCFG.SEEK}\n" +
"   POWERCFG DISABLE : (0x{:0x}".format(sf.POWERCFG.DISABLE) + f") \t{sf.POWERCFG.DISABLE}\n" +
"   POWERCFG ENABLE  : (0x{:0x}".format(sf.POWERCFG.ENABLE) + f") \t{sf.POWERCFG.ENABLE}\n" +
"    CHANNEL TUNE    : (0x{:0x}".format(sf.CHANNEL.TUNE) + f") \t{sf.CHANNEL.TUNE}\n" +
"    CHANNEL CHAN    : (0x{:0x}".format(sf.CHANNEL.CHAN) + f") \t{sf.CHANNEL.CHAN}\n" +
" SYSCONFIG1 RDSIEN  : (0x{:0x}".format(sf.SYSCONFIG1.RDSIEN) + f") \t{sf.SYSCONFIG1.RDSIEN}\n" +
" SYSCONFIG1 STCIEN  : (0x{:0x}".format(sf.SYSCONFIG1.STCIEN) + f") \t{sf.SYSCONFIG1.STCIEN}\n" +
" SYSCONFIG1 RDS     : (0x{:0x}".format(sf.SYSCONFIG1.RDS) + f") \t{sf.SYSCONFIG1.RDS}\n" +
" SYSCONFIG1 DE      : (0x{:0x}".format(sf.SYSCONFIG1.DE) + f") \t{sf.SYSCONFIG1.DE}\n" +
" SYSCONFIG1 AGCD    : (0x{:0x}".format(sf.SYSCONFIG1.AGCD) + f") \t{sf.SYSCONFIG1.AGCD}\n" +
" SYSCONFIG1 BLNDADJ : (0x{:0x}".format(sf.SYSCONFIG1.BLNDADJ) + f") \t{sf.SYSCONFIG1.BLNDADJ}\n" +
" SYSCONFIG1 GPIO3   : (0x{:0x}".format(sf.SYSCONFIG1.GPIO3) + f") \t{sf.SYSCONFIG1.GPIO3}\n" +
" SYSCONFIG1 GPIO2   : (0x{:0x}".format(sf.SYSCONFIG1.GPIO2) + f") \t{sf.SYSCONFIG1.GPIO2}\n" +
" SYSCONFIG1 GPIO1   : (0x{:0x}".format(sf.SYSCONFIG1.GPIO1) + f") \t{sf.SYSCONFIG1.GPIO1}\n" +
" SYSCONFIG2 SEEKTH  : (0x{:0x}".format(sf.SYSCONFIG2.SEEKTH) + f") \t{sf.SYSCONFIG2.SEEKTH}\n" +
" SYSCONFIG2 BAND    : (0x{:0x}".format(sf.SYSCONFIG2.BAND) + f") \t{sf.SYSCONFIG2.BAND}\n" +
" SYSCONFIG2 SPACE   : (0x{:0x}".format(sf.SYSCONFIG2.SPACE) + f") \t{sf.SYSCONFIG2.SPACE}\n" +
" SYSCONFIG2 VOLUME  : (0x{:0x}".format(sf.SYSCONFIG2.VOLUME) + f") \t{sf.SYSCONFIG2.VOLUME}\n" +
" SYSCONFIG3 SMUTER  : (0x{:0x}".format(sf.SYSCONFIG3.SMUTER) + f") \t{sf.SYSCONFIG3.SMUTER}\n" +
" SYSCONFIG3 SMUTEA  : (0x{:0x}".format(sf.SYSCONFIG3.SMUTEA) + f") \t{sf.SYSCONFIG3.SMUTEA}\n" +
" SYSCONFIG3 VOLEXT  : (0x{:0x}".format(sf.SYSCONFIG3.VOLEXT) + f") \t{sf.SYSCONFIG3.VOLEXT}\n" +
" SYSCONFIG3 SKSNR   : (0x{:0x}".format(sf.SYSCONFIG3.SKSNR) + f") \t{sf.SYSCONFIG3.SKSNR}\n" +
" SYSCONFIG3 SKCNT   : (0x{:0x}".format(sf.SYSCONFIG3.SKCNT) + f") \t{sf.SYSCONFIG3.SKCNT}\n")

    def setRegion(self):
        """
        Set the region and channel spacing for the radio configuration.

        This method sets the region and channel spacing for the radio's
        configuration. It updates the relevant fields in the radio's registers
        to match the specified values.

        Note: This method assumes the existence of various methods and
        attributes like `self.setRegs()`, which are supposed to be defined
        elsewhere in the class.

        Example usage:
        ```
        radio.setRegion()
        ```

        Returns:
            None
        """
        # Set the band and channel spacing:
        self.fields.SYSCONFIG2.BAND = self.band
        self.fields.SYSCONFIG2.SPACE = self.channel_space

        # Configure SKSNR and SKCNT fields:
        self.fields.SYSCONFIG3.SKSNR = 1
        self.fields.SYSCONFIG3.SKCNT = 1

        # Disable GPIO1 / 2 to save power:
        self.fields.SYSCONFIG1.GPIO1 = 2
        self.fields.SYSCONFIG1.GPIO2 = 2

        # Update the radio's registers with the new configuration:
        self.setRegs()

    def getRSSI(self):
        """
        Get the Received Signal Strength Indicator (RSSI) value.

        This method returns the Received Signal Strength Indicator (RSSI) value
        from the radio's registers.

        Note: This method assumes the existence of various attributes like
        `self.fields`, which are supposed to be defined elsewhere in the class.

        Example usage:
        ```
        rssi_value = radio.getRSSI()
        print(f"RSSI: {rssi_value}")
        ```

        Returns:
            int: The RSSI value.
        """
        return self.fields.STATUSRSSI.RSSI

    def reset(self):
        """
        Reset the SI470X radio module.

        This method performs the necessary steps to reset the SI470X radio
        module into I2C mode by manipulating the reset pin.

        Note: This method assumes the existence of various attributes like
        `self.reset_pin`, `self.getRegs()`, which are supposed to be defined
        elsewhere in the class.

        Example usage:
        ```
        radio.reset()
        ```

        Returns:
            None
        """
        reset_pin = self.reset_pin
        reset_pin.init(machine.Pin.OUT)
        reset_pin.on()
        # Pin glitches at start up. Let it settle:
        time.sleep_ms(5)
        # Pull reset low for 1ms:
        reset_pin.off()
        time.sleep_ms(1)
        reset_pin.on()
        time.sleep_ms(5)
        self.getRegs()

    def powerup(self):
        """
        Power up the SI470X radio module.

        This method performs the power-up sequence for the SI470X radio module,
        including setting various configuration registers and enabling the
        radio functionality.

        Note: This method assumes the existence of various attributes like
        `self.fields`, `self.setRegs()`, `self.setRegion()`, `self.getRegs()`,
        which are supposed to be defined elsewhere in the class.

        Example usage:
        ```
        radio.powerup()
        ```

        Returns:
            None
        """
        self.getRegs()
        # Enable audio output and power up:
        self.fields.POWERCFG.DMUTE = 1
        self.fields.POWERCFG.ENABLE = 1
        self.fields.POWERCFG.DISABLE = 0
        self.setRegs()
        time.sleep_ms(110)
        self.getRegs()
        self.setRegion()

        # Uncomment and adjust configuration settings if needed:
        # self.fields.SYSCONFIG1.RDS = 1
        # self.fields.SYSCONFIG1.DE = 1
        # self.fields.SYSCONFIG2.SEEKTH = 12
        # self.fields.SYSCONFIG2.BAND = BAND_76_108
        # self.fields.SYSCONFIG2.SPACE = SPACE_100
        # self.fields.SYSCONFIG3.SKSNR = 4
        # self.fields.SYSCONFIG3.SKCNT = 15
        # self.setRegs()

    def powerdown(self):
        """
        Power down the SI470X radio module.

        This method performs the power-down sequence for the SI470X radio
        module, including setting various configuration registers to power
        down different components of the module.

        Note: This method assumes the existence of various attributes like
        `self.fields`, `self.setRegs()`, `self.getRegs()`, which are supposed
        to be defined elsewhere in the class.

        Example usage:
        ```
        radio.powerdown()
        ```

        Returns:
            None
        """
        self.getRegs()

        # Disable audio output and enable analog high-impedance mode:
        self.fields.TEST1.AHIZEN = 1
        self.setRegs()

        self.getRegs()
        # Disable GPIO1, GPIO2, and GPIO3 to save power:
        self.fields.SYSCONFIG1.GPIO1 = 2
        self.fields.SYSCONFIG1.GPIO2 = 2
        self.fields.SYSCONFIG1.GPIO3 = 2
        self.setRegs()

        self.getRegs()
        # Disable audio output, enable power-down mode, and disable module:
        self.fields.POWERCFG.DMUTE = 0
        self.fields.POWERCFG.ENABLE = 1
        self.fields.POWERCFG.DISABLE = 1
        self.setRegs()

    def initialize(self):
        """
        Initialize the SI470X radio module.

        This method performs the initialization sequence for the SI470X radio
        module, including enabling the oscillator and performing the power-up
        sequence.

        Note: This method assumes the existence of various attributes like
        `self.fields`, `self.setRegs()`, `self.getRegs()`, which are supposed
        to be defined elsewhere in the class.

        Example usage:
        ```
        radio.initialize()
        ```

        Returns:
            None
        """
        self.getRegs()

        # Enable oscillator as per AN230, pg 12
        # Despite only *really* wanting to enable the oscillator (XOSCEN), the
        # datasheet states "it is safe to assume that the value of bits
        # [13:0] are 0x0100 prior to power up and are 0x3C04 after.  Given the
        # high number of errata in the documentation of this chip, I've learned
        # that many "MAY" sounding statements are actually "MUST":
        self.fields.TEST1_REG = 0x8100
        self.setRegs()

        time.sleep(0.5)  # Recommended delay.
        self.getRegs()

        time.sleep(0.05)
        self.powerup()

    def tuneChannel(self, chan):
        """
        Tune to the specified channel.

        This method tunes the radio module to the specified channel.

        Args:
            chan (int): The channel frequency to tune to.

        Note: This method assumes the existence of various attributes like
        `self.fields`, `self.setRegs()`, `self.waitAndFinishTune()`,
        which are supposed to be defined elsewhere in the class.

        Example usage:
        ```
        radio.tuneChannel(101)  # Tune to channel 101
        ```

        Args:
            chan (int): The channel frequency to tune to.

        Returns:
            None
        """
        self.fields.CHANNEL.TUNE = 1
        self.fields.CHANNEL.CHAN = chan
        self.setRegs()
        time.sleep_ms(60)
        self.waitAndFinishTune()

    def tuneFreq(self, freq):
        """
        Tune to the specified frequency.

        This method tunes the radio module to the specified frequency.

        Args:
            freq (float): The frequency to tune to.

        Note: This method assumes the existence of various attributes like
        `self.fields`, `self.setRegs()`, `self.waitAndFinishTune()`,
        which are supposed to be defined elsewhere in the class.

        Args:
            freq (float): The frequency to tune to.

        Returns:
            float: The frequency that was set.
        """
        self.getRegs()

        # Determine the valid frequency range and spacing based on the
        # selected band:
        band_range = [(87.5, 107.0), (76.0, 108.0), (76.0, 90.0)][self.fields.SYSCONFIG2.BAND]
        spacing = [0.2, 0.1, 0.05][self.fields.SYSCONFIG2.SPACE]

        # Calculate the channel number based on the frequency and spacing:
        chan = int(round((freq - band_range[0]) / spacing))

        # Tune to the calculated channel:
        self.fields.CHANNEL.TUNE = 1
        self.fields.CHANNEL.CHAN = chan
        self.setRegs()
        time.sleep_ms(60)
        self.waitAndFinishTune()

        # Returning the frequency that was set:
        # Note: Added this so at initalization I can just grab the frequency a
        # little easier. Not sure if this was ok to do as the method didn't
        # return anything before:
        return freq

    def getRegs(self):
        """
        Read and retrieve the current register values from the radio module.

        This method reads the current register values from the radio module and
        returns them as a list.

        Note: This method assumes the existence of various attributes like
        `self.buffer`, `self.i2c`, `self.i2c_addr`, which are supposed to be
        defined elsewhere in the class.

        Returns:
            list: A list containing the current register values.
        """
        result = self.buffer

        # Read register values from the radio module via I2C:
        self.i2c.readfrom_into(self.i2c_addr, result)

        regs = []
        for r in range(16):
            # si4702 returns registers as 10-15, then 0-9, big-endian:
            reg_index = (r + 6) % 16
            # Combine the two bytes of each register to form the register
            # value:
            reg_value = 256 * result[2 * reg_index] + result[2 * reg_index + 1]
            regs.append(reg_value)

        # Store the retrieved register values in the instance variable
        # `self.regs`:
        self.regs = regs

        # Return the list of register values
        return regs

    def seekUp(self):
        """
        Initiate the seeking upwards operation.

        This method sets the appropriate registers to initiate the seeking
        upwards operation on the radio module.

        Note: This method assumes the existence of various attributes like
        `self.fields`, `self.setRegs()`, and `self.waitAndFinishTune()`, which
        are supposed to be defined elsewhere in the class.

        Returns:
            None
        """
        # Set the SEEKUP and SEEK bits to initiate the seeking upwards
        # operation:
        self.fields.POWERCFG.SEEKUP = 1
        self.fields.POWERCFG.SEEK = 1

        # Update the registers with the new configuration:
        self.setRegs()

        # Wait for the seeking operation to complete:
        self.waitAndFinishTune()

    def seekDown(self):
        """
        Initiate the seeking downwards operation.

        This method sets the appropriate registers to initiate the seeking
        downwards operation on the radio module.

        Note: This method assumes the existence of various attributes like
        `self.fields`, `self.setRegs()`, and `self.waitAndFinishTune()`, which
        are supposed to be defined elsewhere in the class.

        Returns:
            None
        """
        # Set the SEEKUP bit to 0 and SEEK bit to 1 to initiate the seeking
        # downwards operation:
        self.fields.POWERCFG.SEEKUP = 0
        self.fields.POWERCFG.SEEK = 1

        # Update the registers with the new configuration:
        self.setRegs()

        # Wait for the seeking operation to complete:
        self.waitAndFinishTune()

    def getFreq(self):
        """
        Get the current tuned frequency.

        This method reads the necessary registers to obtain the high and low
        parts of the frequency information, calculates the frequency using a
        provided formula, and returns the current tuned frequency.

        Note: This method assumes the existence of various attributes like
        `self.fields` and `self.getRegs()`, which are supposed to be defined
        elsewhere in the class.

        Returns:
            int: The current tuned frequency in kHz.
        """
        # Read the necessary registers to obtain frequency information:
        self.getRegs()
        readchan_fields = self.fields.READCHAN

        # Extract the high and low parts of the frequency information:
        freq_high = readchan_fields.BLERB
        freq_low = readchan_fields.READCHAN

        # Calculate the frequency using the provided formula:
        frequency = (freq_high << 8) | freq_low
        frequency *= 2

        return frequency

    def setRegs(self):
        """
        So we've got the buffer which has it's freaky read layout...
        Of course this device also has a goofy write process.
        As per the datasheet regarding read operations:
            An internal address counter automatically increments to allow
            continuous data byte reads, starting with the upper byte of
            register 0Ah, followed by the lower byte of register 0Ah, and
            onward until the lower byte of the last register is reached. The
            internal address counter then automatically wraps around to the
            upper byte of register 00h and proceeds from there until
            continuous reads cease.

        In other words, all reads begin at 0x0A, proceed through 0x0F, & then
        wrap through 0x00 and onto 0x09.

        As to writes, it says:
            An internal address counter automatically increments to allow
            continuous data byte writes, starting with the upper byte of
            register 02h, followed by the lower byte of register 02h, and
            onward until the lower byte of the last register is reached. The
            internal address counter then automatically wraps around to the
            upper byte of register 00h and proceeds from there until
            continuous writes end.

        In other words, all writes begin at 0x02, proceed through 0x0F,
        and then wrap through 0x00 and onto 0x01.

        To me that's a really stupid way of framing what needs to occur.

        Considering that registers 0x0A - 0x0F as well as 0x00 & 0x01 are
        read-only there isn't much point in trying to write past 0x09,
        regardless of any wrapping which may occur.  Looking at the datasheet
        further though we also find the following note on registers 0x08
        and 0x09:
          If written, these bits should be read first and then written with
          their pre-existing values. Do not write during powerup.

        In other words, we really don't care about anything after register
        0x07.  Now, we do our math...

        We have a bytearray of 32 bytes to represent our 16 I2C registers.
        Each register is 16 bits wide, so we'll treat every two bytes as
        representing a single register.

                             +---------+---------+
              Register 0x00  | byte 0  | byte 1  |
                             +---------+---------+
              Register 0x01  | byte 2  | byte 3  |
                             +---------+---------+
                             ~~~~~~~~~~~~~~~~~~~~~
                             +---------+---------+
              Register 0x0F  | byte 30 | byte 31 |
                             +---------+---------+

        To make things easy, we're going to just slurp the contents of the
        registers directly into the bytearray.  Of course, that's where the
        detail noted earlier about the read offset comes in.  Thus, the
        representation inside of the bytearray of the data read from the
        registers is _actually_:

                             +---------+---------+
              Register 0x0A  | byte 0  | byte 1  |
                             +---------+---------+
              Register 0x0B  | byte 2  | byte 3  |
                             +---------+---------+
                             ~~~~~~~~~~~~~~~~~~~~~
                             +---------+---------+
              Register 0x01  | byte 30 | byte 31 |
                             +---------+---------+
        Thus, to reference the map in the datasheet for reads one would use:
           self.buffer[0x0C:]+self.buffer[0:0x0C]

        Correspondingly, for writes, since we only want to write registers 2
        through 7 for a total of 12 bytes we will use:
           self.buffer[0x10:0x1C]
        """

        return self.i2c.writeto(self.i2c_addr, self.buffer[0x10:0x1C])

    def getVolume(self):
        """
        Get the current volume level.

        This method reads the necessary registers to obtain the volume level,
        and returns the current volume level.

        Note: This method assumes the existence of various attributes like
        `self.fields` and `self.getRegs()`, which are supposed to be defined
        elsewhere in the class.

        Returns:
            int: The current volume level.
        """
        # Read the necessary registers to obtain the volume information:
        self.getRegs()

        # Extract and return the volume level:
        return self.fields.SYSCONFIG2.VOLUME

    def getVolume(self):
        """
        Get the current volume level.

        This method reads the necessary registers to obtain the volume level,
        and returns the current volume level.

        Note: This method assumes the existence of various attributes like
        `self.fields` and `self.getRegs()`, which are supposed to be defined
        elsewhere in the class.

        Returns:
            int: The current volume level.
        """
        # Read the necessary registers to obtain the volume information:
        self.getRegs()

        # Extract and return the volume level from the relevant field in
        # SYSCONFIG2:
        return self.fields.SYSCONFIG2.VOLUME

    def setVolume(self, vol):
        """
        Set the volume level.

        This method allows you to set the volume level to the specified value.
        It performs the necessary operations to adjust the volume level within
        the valid range and updates relevant registers accordingly.

        Args:
            vol (int): The desired volume level.

        Note: This method assumes the existence of various attributes like
        `self.fields`, `self.setRegs()`, and others, which are supposed to be
        defined elsewhere in the class.

        Returns:
            bool: True if the volume was successfully set, False otherwise.
        """
        # self.getRegs()

        # Ensure volume level is within valid range:
        if vol < 0:
            vol = 0
        if vol > 15:
            vol = 15

        # Toggle the DMUTE flag based on the volume level:

        # self.regs[6] &= 0xFEFF  # !VOLEXT
        if vol:
            # self.regs[POWERCFG] |= 0xC000  # DSMUTE | DMUTE
            self.fields.POWERCFG.DMUTE = 1
        else:
            # self.regs[POWERCFG] &= 0x3FFF  # !(DSMUTE | DMUTE)
            self.fields.POWERCFG.DMUTE = 0

        # Update the volume level in the relevant field of SYSCONFIG2:

        # Volume is bottom nibble of reg 5
        # self.regs[SYSCONFIG2] = (self.regs[SYSCONFIG2] & 0xFFF0) + vol
        self.fields.SYSCONFIG2.VOLUME = vol

        # Update the registers with the new volume settings:
        success = self.setRegs()

        # Update the internal volume attribute:
        self.volume = vol

        # Return the success status of updating the registers:
        return success

    def changeVolume(self, delta):
        """
        Adjust the volume level by a specified delta.

        This method allows you to increment or decrement the volume level by a
        given delta. It calls the `setVolume` method to update the volume level
        while ensuring it remains within the valid range.

        Args:
            delta (int): The change in volume level. Positive values increase
                         the volume, and negative values decrease it.

        Note: This method assumes the existence of the `self.setVolume` method
        and attributes like `self.volume`, which are defined above this method.

        Returns:
            None
        """
        # Calculate the new volume level after applying the delta:
        new_volume = self.volume + delta

        # Adjust and set the new volume level using the setVolume method:
        self.setVolume(new_volume)

    def seekUpPressed(self):
        """
        Handle the action when the seek up button is pressed.

        This method performs the following actions:
        1. Debounces the seek up button press.
        2. Performs the seek up operation.
        3. Reads the power level and converts it to the corresponding frequency
           using a formula.
        4. Displays the current frequency and additional information on the
           display.
        5. Waits for the seek up button to be released.

        Note: This method assumes the existence of `self.seekUpButton`,
        `self.seekUp()`, `self.fields.READCHAN.BLERB`, `self.getFreq()`,
        and `display` instance (assumed to be a global variable).

        Example usage:
        ```
        instance = SomeClass()
        instance.seekUpPressed()
        ```
        """
        if self.seekUpButton.debounce():
            print('Seeking up...')
            self.seekUp()

            power_level = self.fields.READCHAN.BLERB
            current_freq = self.getFreq()
            # Calculate the frequency in MHz:
            freq_mhz = (87.5 + current_freq * 0.1)

            display.clear()
            display.show_text('Listening to:',
                              f'{freq_mhz:.1f} MHz', # Format/display the freq.
                              'B1 = Vol Up',
                              'B2 = Vol Down',
                              'B3 = Seek Up',
                              'B4 = Seek Down')

            while self.seekUpButton.pin.value() == 0:
                pass

    def seekDownPressed(self):
        """
        Handle the action when the seek down button is pressed.

        This method performs the following actions:
        1. Debounces the seek down button press.
        2. Performs the seek down operation.
        3. Reads the power level and converts it to the corresponding frequency
           using a formula.
        4. Displays the current frequency and additional information on the
           display.
        5. Waits for the seek down button to be released.

        Note: This method assumes the existence of `self.seekDownButton`,
        `self.seekDown()`, `self.fields.READCHAN.BLERB`, `self.getFreq()`,
        and `display` instance (assumed to be a global variable).

        Example usage:
        ```
        instance = SomeClass()
        instance.seekDownPressed()
        ```
        """
        if self.seekDownButton.debounce():
            print('Seeking down...')
            self.seekDown()

            power_level = self.fields.READCHAN.BLERB
            current_freq = self.getFreq()
            # Calculate the frequency in MHz:
            freq_mhz = (87.5 + current_freq * 0.1)

            display.clear()
            display.show_text('Listening to:',
                              f'{freq_mhz:.1f} MHz', # Format/display the freq.
                              'B1 = Vol Up',
                              'B2 = Vol Down',
                              'B3 = Seek Up',
                              'B4 = Seek Down')

            while self.seekDownButton.pin.value() == 0:
                pass

    def volumeDownPressed(self):
        """
        Handle the action when the volume down button is pressed.

        This method performs the following actions:
        1. Debounces the volume down button press.
        2. Prints messages related to volume control.
        3. Adjusts the volume if it's not already at the minimum level.
        4. Waits for the volume down button to be released.

        Note: This method assumes the existence of `self.volumeDownButton` and
        `self.getVolume()` and `self.setVolume()` methods.

        Example usage:
        ```
        instance = SomeClass()
        instance.volumeDownPressed()
        ```
        """
        # Debounce the button press:
        if self.volumeDownButton.debounce():
            print('Volume down...')
            current_volume = self.getVolume()
            print(current_volume)

            # Check if volume is already at the minimum level:
            if current_volume == 0:
                print('Volume is already 0...')
            else:
                print('Decreasing volume...')
                self.setVolume(current_volume - 1)

            # Wait for the volume down button to be released:
            while self.volumeDownButton.pin.value() == 0:
                pass

    def volumeUpPressed(self):
        """
        Handle the action when the volume up button is pressed.

        This method performs the following actions:
        1. Debounces the volume up button press.
        2. Prints messages related to volume control.
        3. Adjusts the volume if it's not already at the maximum level.
        4. Waits for the volume up button to be released.

        Note: This method assumes the existence of `self.volumeUpButton` and
        `self.getVolume()` and `self.setVolume()` methods.

        Example usage:
        ```
        instance = SomeClass()
        instance.volumeUpPressed()
        ```
        """
        # Debounce the button press:
        if self.volumeUpButton.debounce():
            print('Volume up...')
            current_volume = self.getVolume()
            print(current_volume)

            # Check if volume is already at the maximum level:
            if current_volume == 15:
                print('Volume is already 15...')
            else:
                print('Increasing volume...')
                self.setVolume(current_volume + 1)

            # Wait for the volume up button to be released:
            while self.volumeUpButton.pin.value() == 0:
                pass

# Usage:

# Initialize the radio:
radio = SI470X()

# Set the volume to max (15):
radio.setVolume(15)

# Tune to and save the current frequency:
current_freq = str(radio.tuneFreq(103.3))

# Initialize the OLED display:
display = SSD1306(128, 64, sda_pin=5, scl_pin=23)

# Display the current frequency and button legend:
display.show_text('Listening to:',
                  current_freq + 'FM',
                  'B1 = Vol Up',
                  'B2 = Vol Down',
                  'B3 = Seek Up',
                  'B4 = Seek Down')

# GPIO's for the buttons are as follows:
# VOL_UP=4, VOL_DN=14, SEEK_UP=15, SEEK_DOWN=13

# Print button maps:
print('Four buttons arranged from left to right.')
print('Button 1 - Volume Up')
print('Button 2 - Volume Down')
print('Button 3 - Seek Up')
print('Button 4 - Seek Down')
