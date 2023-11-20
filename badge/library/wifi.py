import network
import ubinascii
import uasyncio as asyncio
import utime  # MicroPython module for time functions

class WiFiManager:
    def __init__(self, ssid, password):
        """
        Initalize the WiFiManager class - this class is used to connect to a WiFi network
        :param ssid: The SSID of the WiFi network to connect to
        :param password: The password of the WiFi network to connect to
        """
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    async def connect(self):
        """
        Connect to the WiFi network
        :return: None
        """
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print('Connecting to network...')
            self.wlan.connect(self.ssid, self.password)
        return True if self.wlan.isconnected() else False

    async def get_status(self):
        """
        Get the status of the WiFi connection
        :return: A tuple containing the status of the WiFi connection
        """
        return self.wlan.ifconfig()

    def isWifiConnected(self):
        """
        Check if the WiFi is connected
        :return: True if connected, False if not connected
        """
        return True if self.wlan.isconnected() else False

    def get_mac(self):
        """
        Get the MAC address of the WiFi interface

        :return: The MAC address of the WiFi interface
        """
        return ubinascii.hexlify(self.wlan.config('mac'),':').decode()

    def get_wifi_strength(self):
        """
        Get the WiFi signal strength

        :return: The WiFi signal strength
        """
        return int(self.wlan.status('rssi'))
