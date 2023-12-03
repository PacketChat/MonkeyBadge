import config
import urequests as requests
import network


class CLI:
    def __init__(self, badge) -> None:
        self.cmds = {
            "help": "Display Help Menu!",
            "debug": "Turn on/off debug logging mode",
            "factory_reset": "Clear the badge database and server data",
            "rename": "Change your badge handle",
            "about": "About this badge",
            "net": "Display network information",
            "state": "Display badge state",
            "recover": "Recover badge state from server. IF you haven't done a reset.",
            "set_wifi": "Set the wifi credentials",
        }
        if badge:
            self.token = badge.apitoken
            self.uuid = badge.badge_uuid
            self.radio = badge.radio
            self.gameclient = badge.gameclient
            self.handle = badge.handle
            self.version = badge.version
            self.db = badge.db
            self.gameclient = badge.gameclient

    def debug_cmd(self, arg):
        if arg == "off":
            # self.logging.basicConfig(level=self.logging.ERROR)
            print("Logging level set to ERROR only.")
        elif arg == "on":
            # self.logging.basicConfig(level=self.logging.DEBUG)
            print("Logging level set to DEBUG.")
        else:
            print("Unknown debug argument. Try 'on' or 'off'")

    def printhelp(self):
        print("BadgeCLI Commands:")
        for k, v in self.cmds.items():
            print(f" {k} - {v}")

    def execute_command(self, command):
        if command:
            parts = command.split()

            if parts[0]:
                cmd = parts[0]
                if len(parts) == 2:
                    arg = parts[1]
                else:
                    arg = None
            else:
                print("Unknown command, try 'help'")
                return

            if cmd == "debug":
                if arg:
                    self.debug_cmd(arg)
                else:
                    print("try: debug [on|off]")
            elif cmd == "state":
                self.getbadgestate()
            elif cmd == "help":
                self.printhelp()
            elif cmd == "rename":
                if arg:
                    self.rename(arg)
                else:
                    print("try: rename [newname]")
            elif cmd == "net":
                self.display_network()
            elif cmd == "factory_reset":
                self.factory_reset()
            elif cmd == "recover":
                if arg:
                    self.recover_badge()
                else:
                    print("try: recover [token]")
            elif cmd == "about":
                self.display_about()
            else:
                print("Unknown command, try 'help'")

    def getbadgestate(self):
        try:
            j = self.db.get("state")
            if j:
                print("Badge State:")
                print(j)
        except KeyError:
            print("Badge is not registered.")

    def recover_badge(self, token=""):
        if not token:
            print("you will need your api-token to recover your badge.")
            print("ONLY DO THIS IF AT THE RECOMMENDATION OF AN ADMIN")
            print("your api-token can be recovered by admins")
            print("try: recover [token]")
            return

        print("Recovering Badge State from Server")
        self.db.set("token", {"token": token})
        print("Badge State will recover on next check-in")

    def display_about(self):
        print(f"MonkeyBadge Version {self.version}")
        print(f" UUID: {self.uuid}")
        print(f" Handle: {self.handle}")

    def rename(self, name=""):
        if not name:
            print("try: rename [newname]")
            return
        if not self.db.get("state"):
            self.gameclient.change_handle(self.token, self.uuid, name)
            print("changed name to: ", name)
        else:
            print("Badge is not registered.")

    def run(self):
        while True:
            c = input("BadgeCLI> ").strip()
            self.execute_command(c)

    def factory_reset(self):
        if not self.token:
            print("Badge is not registered.")
            return

        print("Factory reset will delete the local badge Database AND the server data.")
        print("THIS IS NOT RECOVERABLE.")
        s = input(
            "Do type 'THISWILLDELETEBADGE' to confirm, or anything else to cancel."
        )
        if s == "THISWILLDELETEBADGE":
            # this should exist in the gameclient module
            r = input("Type: 'THISWILLDELETEBADGE' to confirm: ")
            if r == "THISWILLDELETEBADGE":
                header = {"X-API-Key": self.token}
                url = f"{config.API_SERVER}/deletebadge"
                request = {"myUUID": self.uuid, "key": "THISWILLDELETEBADGE"}
                # print(f"Sending request to {config.API_SERVER}/deletebadge")
                # print(f"Header: {header} Request: {request}")
                r = requests.post(url, headers=header, json=request)

                # os.remove("badgedb")
            print("Factory reset complete")
            return

    def display_network(self):
        wlan = network.WLAN(network.STA_IF)
        rssi = wlan.status("rssi")
        t = wlan.ifconfig()
        print("Network Information:")
        print(" RSSI: ", rssi)
        print(" IP: ", t[0])
        print(" Netmask: ", t[1])
        print(" Gateway: ", t[2])
        print(" DNS: ", t[3])
