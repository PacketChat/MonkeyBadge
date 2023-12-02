# SI470x control via I2C
from micropython import const
from uctypes import struct, addressof
from uctypes import BF_POS, BF_LEN, UINT16, BFUINT16, BIG_ENDIAN
import time
import machine

BAND_US = const(0)
BAND_JP_WIDE = const(1)
BAND_JP = const(2)

CSPACE_US = const(0)
CSPACE_WORLD = const(1)
CSPACE_NARROW = const(2)

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


class SI470X(object):
    def __init__(
        self,
        i2c=None,
        i2c_addr=0x10,
        reset_pin=machine.Pin(16, machine.Pin.OUT),
        band=BAND_US,
        channel_space=CSPACE_US,
        rds=False,
    ):
        if i2c is None:
            i2c = machine.I2C(
                0,
                scl=machine.Pin(22, machine.Pin.OUT),
                sda=machine.Pin(21, machine.Pin.OUT),
            )
        self.buffer = bytearray(32)
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.reset_pin = reset_pin
        self.band = band
        self.channel_space = channel_space
        self.fields = struct(addressof(self.buffer), SI470X_REGS, BIG_ENDIAN)
        self.volume = 0
        self.muted = False

        # Powerup sequence.
        self.reset()
        self.initialize()

    def waitAndFinishTune(self):
        c = 100
        while (self.fields.STATUSRSSI.STC == 0) & (c > 0):
            self.getRegs()
            time.sleep_ms(100)
            c -= 1
        if c < 1:
            print("Countdown expired.")
        self.fields.POWERCFG.SEEK = 0
        self.fields.CHANNEL.TUNE = 0
        self.setRegs()
        c = 100
        while (self.fields.STATUSRSSI.STC != 0) & (c > 1):
            self.getRegs()
            time.sleep_ms(100)
            c -= 1
        if c < 1:
            print("Countdown expired.")

    def getStatus(self):
        # This is just a little funkiness to try and squeeze most of this onto
        # a single screen.  Basically we bind "self.fields" to a shorter
        # variable name solely within the scope of the function.

        sf = self.fields
        # fmt: off
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

    # fmt: on

    def setRegion(self):
        self.fields.SYSCONFIG2.BAND = self.band

        self.fields.SYSCONFIG2.SPACE = self.channel_space

        self.fields.SYSCONFIG3.SKSNR = 1
        self.fields.SYSCONFIG3.SKCNT = 1

        # Disable GPIO1 / 2  to save power
        self.fields.SYSCONFIG1.GPIO1 = 2
        self.fields.SYSCONFIG1.GPIO2 = 2
        self.setRegs()

    def getRSSI(self):
        return self.fields.STATUSRSSI.RSSI

    def reset(self):
        # Boot si4703 into i2c mode by pulling reset low while i2c SDA is low.
        reset_pin = self.reset_pin
        reset_pin.init(machine.Pin.OUT)
        reset_pin.on()
        # Pin glitches at start up.  Let it settle.
        time.sleep_ms(5)
        # Pull reset low for 1ms.
        reset_pin.off()
        time.sleep_ms(1)
        reset_pin.on()
        time.sleep_ms(5)
        self.getRegs()

    def powerup(self):
        # After RdSpi/si4703.c:si_power().
        self.getRegs()
        # self.regs[POWERCFG]    = 0x4001  # PWR_ENABLE
        self.fields.POWERCFG.DMUTE = 1
        self.fields.POWERCFG.ENABLE = 1
        self.fields.POWERCFG.DISABLE = 0
        self.setRegs()
        time.sleep_ms(110)
        self.getRegs()
        self.setRegion()

        # self.regs[SYSCONFIG1] |= 0x1800  # RDS | DE
        # self.regs[SYSCONFIG1] &= 0xFF3F  # !BLNDADJ
        # self.regs[SYSCONFIG2]  = 0x0C10  # SEEKTH12 | BAND0 | SPACE100
        # self.regs[SYSCONFIG3] &= 0xFF00
        # self.regs[SYSCONFIG3] |= 0x024F  # RDSPRF | SKSNR 4, SKCNT 15

    def powerdown(self):
        self.getRegs()
        self.fields.TEST1.AHIZEN = 1
        self.setRegs()

        self.getRegs()
        self.fields.SYSCONFIG1.GPIO1 = 2
        self.fields.SYSCONFIG1.GPIO2 = 2
        self.fields.SYSCONFIG1.GPIO3 = 2
        self.setRegs()

        self.getRegs()
        self.fields.POWERCFG.DMUTE = 0
        self.fields.POWERCFG.ENABLE = 1
        self.fields.POWERCFG.DISABLE = 1
        self.setRegs()

    def initialize(self):
        self.getRegs()
        # Enable oscillator as per AN230, pg 12
        # Despite only *really* wanting to enable the oscillator (XOSCEN), the
        # datasheet states "it is safe to assume that the value of bits
        # [13:0] are 0x0100 prior to power up and are 0x3C04 after.  Given the
        # high number of errata in the documentation of this chip, I've learned
        # that many "MAY" sounding statements are actually "MUST".
        # self.fields.TEST1.XOSCEN = 1
        self.fields.TEST1_REG = 0x8100
        self.setRegs()
        time.sleep(0.5)  # recommended delay.
        self.getRegs()

        time.sleep(0.05)
        self.powerup()

    def tuneChannel(self, chan):
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
        band_range = [(87.5, 107.0), (76.0, 108.0), (76.0, 90.0)][
            self.fields.SYSCONFIG2.BAND
        ]
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
        result = self.buffer
        self.i2c.readfrom_into(self.i2c_addr, result)
        regs = []
        for r in range(16):
            # si4702 returns registers as 10-15, then 0-9, big-endian.
            reg_index = (r + 6) % 16
            regs.append(256 * result[2 * reg_index] + result[2 * reg_index + 1])
        self.regs = regs
        return regs

    def setRegs(self):
        # So we've got the buffer which has it's freaky read layout...
        # Of course this device also has a goofy write process.
        # As per the datasheet regarding read operations:
        #     An internal address counter automatically increments to allow
        #     continuous data byte reads, starting with the upper byte of
        #     register 0Ah, followed by the lower byte of register 0Ah, and
        #     onward until the lower byte of the last register is reached. The
        #     internal address counter then automatically wraps around to the
        #     upper byte of register 00h and proceeds from there until
        #     continuous reads cease.
        #
        # In other words, all reads begin at 0x0A, proceed through 0x0F, & then
        # wrap through 0x00 and onto 0x09.
        #
        # As to writes, it says:
        #     An internal address counter automatically increments to allow
        #     continuous data byte writes, starting with the upper byte of
        #     register 02h, followed by the lower byte of register 02h, and
        #     onward until the lower byte of the last register is reached. The
        #     internal address counter then automatically wraps around to the
        #     upper byte of register 00h and proceeds from there until
        #     continuous writes end.
        #
        #
        # In other words, all writes begin at 0x02, proceed through 0x0F,
        # and then wrap through 0x00 and onto 0x01.

        # To me that's a really stupid way of framing what needs to occur.
        #
        # Considering that registers 0x0A - 0x0F as well as 0x00 & 0x01 are
        # read-only there isn't much point in trying to write past 0x09,
        # regardless of any wrapping which may occur.  Looking at the datasheet
        # further though we also find the following note on registers 0x08
        # and 0x09:
        #   If written, these bits should be read first and then written with
        #   their pre-existing values. Do not write during powerup.
        #
        # In other words, we really don't care about anything after register
        # 0x07.  Now, we do our math...
        #
        # We have a bytearray of 32 bytes to represent our 16 I2C registers.
        # Each register is 16 bits wide, so we'll treat every two bytes as
        # representing a single register.
        #
        #                      +---------+---------+
        #       Register 0x00  | byte 0  | byte 1  |
        #                      +---------+---------+
        #       Register 0x01  | byte 2  | byte 3  |
        #                      +---------+---------+
        #                      ~~~~~~~~~~~~~~~~~~~~~
        #                      +---------+---------+
        #       Register 0x0F  | byte 30 | byte 31 |
        #                      +---------+---------+
        #
        # To make things easy, we're going to just slurp the contents of the
        # registers directly into the bytearray.  Of course, that's where the
        # detail noted earlier about the read offset comes in.  Thus, the
        # representation inside of the bytearray of the data read from the
        # registers is _actually_:
        #
        #                      +---------+---------+
        #       Register 0x0A  | byte 0  | byte 1  |
        #                      +---------+---------+
        #       Register 0x0B  | byte 2  | byte 3  |
        #                      +---------+---------+
        #                      ~~~~~~~~~~~~~~~~~~~~~
        #                      +---------+---------+
        #       Register 0x01  | byte 30 | byte 31 |
        #                      +---------+---------+
        # Thus, to reference the map in the datasheet for reads one would use:
        #    self.buffer[0x0C:]+self.buffer[0:0x0C]
        #
        # Correspondingly, for writes, since we only want to write registers 2
        # through 7 for a total of 12 bytes we will use:
        #    self.buffer[0x10:0x1C]

        return self.i2c.writeto(self.i2c_addr, self.buffer[0x10:0x1C])

    def getVolume(self):
        self.getRegs()
        # return (self.regs[SYSCONFIG2] & VOLUME_MASK)
        return self.fields.SYSCONFIG2.VOLUME

    def setVolume(self, vol):
        # self.getRegs()
        if vol < 0:
            vol = 0
        if vol > 15:
            vol = 15
        #  self.regs[6] &= 0xFEFF  # !VOLEXT
        if vol:
            # self.regs[POWERCFG] |= 0xC000  # DSMUTE | DMUTE
            self.fields.POWERCFG.DMUTE = 1
        else:
            # self.regs[POWERCFG] &= 0x3FFF  # !(DSMUTE | DMUTE)
            self.fields.POWERCFG.DMUTE = 0
        # Volume is bottom nibble of reg 5
        # self.regs[SYSCONFIG2] = (self.regs[SYSCONFIG2] & 0xFFF0) + vol
        self.fields.SYSCONFIG2.VOLUME = vol

        self.setRegs()
        self.volume = vol

    def getFreq(self):
        # Read the necessary registers to obtain frequency information:
        self.getRegs()
        readchan_fields = self.fields.READCHAN

        # Extract the high and low parts of the frequency information:
        freq_high = readchan_fields.BLERB
        freq_low = readchan_fields.READCHAN

        # Calculate the frequency using the provided formula:
        frequency = (freq_high << 8) | freq_low
        frequency *= 2

        # convert to our band and MHZ
        result = 87.5 + frequency * 0.1

        return f"{result}"

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

    def changeVolume(self, delta):
        self.setVolume(self.volume + delta)

    def mute(self):
        self.setVolume(0)
        self.muted = True

    def unmute(self):
        self.setVolume(5)
        self.muted = False
