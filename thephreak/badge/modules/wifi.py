import network
import ubinascii
import uasyncio as asyncio

class WiFiManager:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    async def connect(self):
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print('Connecting to network...')
            self.wlan.connect(self.ssid, self.password)
            while not self.wlan.isconnected():
                await asyncio.sleep(1)  # non-blocking wait for 1 second
        print('Network config:', self.wlan.ifconfig())

    async def get_status(self):
        return self.wlan.ifconfig()
    
    def isWifiConnected(self):
        return True if self.wlan.isconnected() else False

    def get_mac(self):
        return ubinascii.hexlify(self.wlan.config('mac'),':').decode()
