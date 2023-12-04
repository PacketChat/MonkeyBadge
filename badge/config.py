"""configuration settings"""
from collections import namedtuple

TRANSIT_PERIOD = 5000
# IR Pins (also double as right SAO GPIO pins)
IR_RX_PIN = 19  # SAO2 GPIO1
IR_TX_PIN = 17  # SAO2 GPIO2

IR_TX_DELAY = 175

# HIDDEN OBJECT SPECS
HIDDEN_OBJECTS = {
    1: {"addr": 12341},
    2: {"addr": 42342},
    3: {"addr": 52321},
    4: {"addr": 65001},
    5: {"addr": 38913},
}

Opcode = namedtuple("Opcode", ["code", "additional_bytes"])
IR_OPCODES = {
    "DISCOVER": Opcode(1, 0),
    "HERE": Opcode(2, 0),
    "INIT_PAIR": Opcode(3, 0),
    "RESP_PAIR": Opcode(4, 2),
    "ACK_RESP": Opcode(5, 2),
    "EMOTE": Opcode(6, 3),
    "MONKEY": Opcode(7, 2),
    "HIDDEN_OBJECT": Opcode(8, 2),
}
