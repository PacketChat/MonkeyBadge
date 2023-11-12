from machine import Pin
import time

import config
from ir_tx.nec import NEC as NECTx

class BadMessage(Exception):
    """Raised if a bad message is received"""

class IncompleteMessage(Exception):
    """Raised if message is requested in incomplete state"""

class OverDelay(Exception):
    """Raised if extra byte received past max delay"""

class IRMessage:
    """IR Message Class"""
    def __init__(self, sender, opcode):
        self.last_data_time = time.ticks_ms()
        self.sender = sender
        self.extra = []
        self.bad_message = False
        try:
            self.opcode = config.REV_IR_OPCODES[opcode]
        except KeyError:
            raise BadMessage('unknown opcode')

        self.expected_extra = config.IR_OPCODES[self.opcode].additional_bytes
        if not self.expected_extra:
            self.finished = True

    def append(self, data):
        """Append extra bytes to message, fails if time since last received
            byte is too long
        """
        now = time.ticks_ms()
        # time between messages too high
        if now - self.last_data_time > config.IR_RX_MAX_DELAY:
            raise OverDelay
        # too much data?
        if self.finished:
            raise BadMessage
        self.extra.append(data)
        if len(self.extra) == self.expected_extra:
            self.finished = True

    def message(self):
        """Properly formatted full message

            Returns the name of a handler, the sender, and any associated data
        """
        if not self.finished:
            raise IncompleteMessage('additional data required')
        return self.opcode, self.sender, self.extra

class IR:
    def __init__(self, self_addr):
        self.tx = NECTx(Pin(config.IR_TX_PIN, Pin.Out))
        self.partials = {}
        self.self_addr = self_addr
        self.msgs = []

    def recv(self, addr, data):
        # ignore messages received from my own transmitter
        if addr == self.self_addr:
            return
        try:
            self.partials[addr].append(data)
        except KeyError:
            try:
                self.partials[addr] = IRMessage(addr, data)
            except BadMessage:
                # unknown opcode
                return
        except OverDelay, BadMessage:
            # treat this as a new message
            del self.partials[addr]
            self.recv(addr, data)

        if self.partials[addr].finalized:
            msg = self.partials[addr].message()
            self.msgs.append(msg)
            del self.partials[addr]

    def send(self, data):
        """Send data over IR, data should be a list of uint8"""
        for item in data:
            self.tx.transmit(self.self_addr, item)
            time.sleep_ms(CONFIG.IR_TX_DELAY)
