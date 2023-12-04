import machine
import os

from library.ir import IR

import config  # Import the config file
import monkeyconfig


class HiddenObject:
    def __init__(self):
        """
        Initalize the MonkeyBadge class - this class is used to interact with the
        MonkeyBadge server API

        :param uuid: The UUID of the badge
        """
        self.last_send = 0
        self.my_id = self._discover_id()
        print("my_id:", self.my_id)

        self.infrared = IR(config.HIDDEN_OBJECTS[self.my_id]["addr"])

    def _discover_id(self):
        files = os.listdir("")
        for file in files:
            if file.startswith("ho") and len(file) == 3 and file[2].isdigit():
                return int(file[2])
        raise ValueError("no id found")

    def _broadcast(self):
        self.infrared.send([monkeyconfig.IR_OPCODES["HIDDEN_OBJECT"].code])

    def run(self):
        """game loop"""
        while True:
            self._broadcast()
            machine.lightsleep(config.TRANSIT_PERIOD)
            break
