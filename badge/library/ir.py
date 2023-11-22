"""IR API Layer"""
from machine import Pin
import micropython
import time
import uasyncio as asyncio

import config
from library.ir_tx.nec import NEC as NECTx
from library.ir_rx.nec import NEC_16 as NECRx

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
        self.enabled = False
        self.pairing = False
        self.monkey_mode = False
        self.hiddren_objects = False

        self.tx = NECTx(Pin(config.IR_TX_PIN, Pin.Out))
        self.rx = None
        self.partials = {}
        self.self_addr = self_addr
        self.msgs = []

    def __schedule_recv(self, *args):
        micropython.schedule(self.recv, args)

    def _keep_message(self, opcode, sender, extra):
        opcode_name = config.REV_IR_OPCODES[opcode]
        if opcode_name == 'MONKEY' and not self.monkey_mode:
            return False
        if opcode_name == 'HIDDEN_OBJECT' and not self.hiddren_objects:
            return False
        if opcode_name == 'INIT_PAIR' and not self.pairing:
            return False
        return True

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
        except (OverDelay, BadMessage):
            # treat this as a new message
            del self.partials[addr]
            self.recv(addr, data)

        if self.partials[addr].finalized:
            msg = self.partials[addr].message()
            # filter out non-enabled messages
            if self._keep_message(*msg):
                self.msgs.append(msg)
            del self.partials[addr]

    def send(self, data):
        """Send data over IR, data should be a list of uint8"""
        if not self.enabled:
            return
        for item in data:
            self.tx.transmit(self.self_addr, item)
            time.sleep_ms(config.IR_TX_DELAY)

    def send_discover(self):
        """Sends a discover packet"""
        data = [config.IR_OPCODES['DISCOVER'].code]
        self.send(data)

    def send_emote(self, dst, emote):
        """Stretch goal: send an emote"""
        data = [config.IR_OPCODES['EMOTE'].code, emote]
        data.extend(dst.to_bytes(2, 'big'))
        self.send(data)

    def initiate_pairing(self):
        """Sends a pairing request"""
        data = [config.IR_OPCODES['INIT_PAIR'].code]
        self.send(data)

    def enable(self):
        """Enable IR Recv"""
        self.enabled = True
        self.rx = NECRx(Pin(config.IR_RX_PIN),
                        self.__schedule_recv)

    def disable(self):
        """Disable IR Recv"""
        self.enabled = False
        self.rx.close()
        self.rx = None

    def enable_monkey_mode(self):
        """Enabled for receiving monkey packets"""
        self.monkey_mode = True

    def enable_hidden_object_mode(self):
        """Enabled for receiving hidden object packets"""
        self.hiddren_objects = True

    def enable_pairing(self):
        self.pairing = True
