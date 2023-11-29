from machine import Pin
import micropython

import urequests as requests
import usocket as socket
import ussl as ssl

import ujson as json
import uasyncio as asyncio

from library.display import DisplayHandler
from library.menu import Menu, MenuItem
from library.leds import LEDHandler
from library.wifi import WiFiManager
from library.button import ButtonHandler
from library.radio import SI470X
from library.db import dbtree
from library.ota.update import OTA as OTAUpdate
import library.ota.rollback as OTARollback

#from library.ir_rx.nec import NEC_16 as NECRx
import config  # Import the config file
import re

class MonkeyBadge:
    def __init__(self):
        """
        Initalize the MonkeyBadge class - this class is used to interact with the MonkeyBadge server API
        :param uuid: The UUID of the badge
        """
        # define URL with factory reset endpoint
        self.reset_url = config.RESET_URL
        self.update_url = config.UPDATE_URL

        # radio init
        self.radio = SI470X()
        self.radio.setVolume(1)
        self.db = dbtree()


        # Wifi Init
        self.wifi_manager = WiFiManager(config.WIFI_SSID, config.WIFI_PASSWORD)

        # Display Init
        self.display = DisplayHandler(config.OLED_WIDTH, config.OLED_HEIGHT, config.OLED_SDA_PIN, config.OLED_SCL_PIN)

        # Led init
        self.leds = LEDHandler()

        # boot
        print("Badge Booting")
        self.display.print_logo()

        #self.leds.do_rainbow_cycle(speed=1)
        self.leds.do_boot_sequence()

        # IR init
        #NECRx(Pin(config.IR_RX_PIN, Pin.IN), self._schedule_ir_input)

        self.registration_key = config.REG_KEY
        self.current_menu = None
        self.ir_enabled = False

        # Need to pull these from the db store.
        self.apitoken = self.db.get("token")
        self.lock_radio_station = False

        self.handle = ""
        self.IR_ID = ""
        self.current_challenge = None
        self.challenge1 = {}
        self.challenge2 = {}
        self.challenge3 = {}
        self.intro = {"intro_complete": False, "intro_enabled": False}

        # use the mac as the UUID
        self.macid = re.sub(':', '-', str(self.wifi_manager.get_mac()))
        self.badge_uuid = self.macid
        print("Badge UUID: %s" % (self.badge_uuid))

        print("Confirming firmware boot success. Cancelling OTA Rollback")
        OTARollback.cancel()

        # Menu Definitions
        self.main_menu = Menu([], title="Main")
        self.radio_menu = Menu([], title="Radio", parent=self.main_menu)
        self.settings_menu = Menu([], title="Settings", parent=self.main_menu)
        self.lightshow_menu = Menu([], title="LED Demos", parent=self.main_menu)
        self.ir_menu = Menu([], title="Infrared", parent=self.main_menu)
        self.about_menu = Menu([], title="About", parent=self.main_menu)

        self.volume_menu = Menu([], title="Volume", parent=self.radio_menu)
        self.volume_menu.items.extend([
            MenuItem("Volume", self.donothing, dynamic_text=self.display_vol),
            MenuItem("Volume Up", self.menu_volume_up),
            MenuItem("Volume Down", self.menu_volume_down)
        ])
        self.main_menu.items.extend([
            MenuItem("Radio", submenu=self.radio_menu),
            MenuItem("Settings", submenu=self.settings_menu),
            MenuItem("Lightshow", submenu=self.lightshow_menu),
            MenuItem("IR", submenu=self.ir_menu),
            MenuItem("About", submenu=self.about_menu)
        ])
        self.about_menu.items.extend([
            MenuItem("Version", "pass"),
            MenuItem("Credits", "pass"),
            MenuItem("License", "pass")
        ])
        self.ir_menu.items.extend([
            MenuItem("Send Message", "pass"),
            MenuItem("Receive Message", "pass")
        ])
        self.radio_menu.items.extend([
            MenuItem("Frequency", self.donothing, dynamic_text=self.display_freq),
            MenuItem("Seek Up", self.menu_seek_up),
            MenuItem("Seek Down", self.menu_seek_down),
            MenuItem("Volume", submenu=self.volume_menu),
        ])
        self.settings_menu.items.extend([
            MenuItem("OLED Brightness", "pass"),
            MenuItem("LED Brightness", "pass"),
            #        MenuItem("Volume", "pass"),
            MenuItem("Debounce", "pass"),
            MenuItem("OTA Update", self.update_badge),
            MenuItem("Reset Badge", self.reset_badge)
        ])
        self.lightshow_menu.items.extend([
            MenuItem("popcorn", self.leds.do_popcorn_effect),
            MenuItem("strobe", self.leds.do_strobe),
            MenuItem("roll call", self.leds.do_monkey_roll_call)
        ])

    def lock_station(self, freq):
        self.lock_radio_station = True
        self.radio.tuneFreq(freq)

    def unlock_station(self, freq):
        self.lock_radio_station = False

    def menu_volume_up(self):
        print(f"Radio volume set to {self.radio.volume}")
        if self.radio.getVolume() < 15:
            self.radio.setVolume(self.radio.volume + 1)
        return self.current_menu

    def menu_volume_down(self):
        if self.radio.volume > 0:
            self.radio.setVolume(self.radio.volume - 1)
        print(f"Radio volume set to {self.radio.volume}")
        return self.current_menu

    def menu_seek_up(self):
        if self.lock_radio_station == False:
            self.radio.seekUp()
            print(f"Radio tuned to {self.radio.getFreq()}")
        return self.current_menu

    def menu_seek_down(self):
        if self.lock_radio_station == False:
            self.radio.seekDown()
            print(f"Radio tuned to {self.radio.getFreq()}")
        return self.current_menu

    def flash_badge(self, url, verbose=False):
        #TODO: change the state of the screen to show that the badge is updating and resetting
        try:
            #print(OTAStatus.status())
            with OTAUpdate(reboot=True, verbose=verbose) as ota:
                ota.from_json(url)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
#            if err == -202:
#                print("Unable to process update: Network Error")
#            else:
#                print("Unable to flash device %s" % (err))

    def update_badge(self):
        print("Applying over the air (OTA) Update...")
        self.display.print_lines(["", "  Applying OTA", "     Update  "])
        self.flash_badge(self.update_url)

    def reset_badge(self):
        import os
        from flashbdev import bdev

        # MicroPython's partition table uses "vfs"
        # This effectively "formats" the flash
        print("Erasing Flash...")
        os.VfsFat.mkfs(bdev)
        print("Erasing Non Volatile Storage (NVS)...")
        config.eraseNVS("API_SERVER")
        config.eraseNVS("WIFI_SSID")
        config.eraseNVS("WIFI_PASSWORD")
        print("Applying Factory Firmware...")
        self.display.print_lines(["", "Applying Factory", "    Firmware"])
        self.flash_badge(self.reset_url)

    def display_freq(self):
        return f"FM: {self.radio.getFreq()}"

    def display_vol(self):
        return f"Volume: {self.radio.volume}"

    def donothing(self):
        return self.current_menu

    def _button_callback(self,button_idx):

        if button_idx == 0:
            index = self.display.menu_up()
            self.current_menu.select(index)
        elif button_idx == 1:
            index = self.display.menu_down()
            self.current_menu.select(index)
        elif button_idx == 2:
            self.select_button()
        elif button_idx == 3:
            self.toggle_mute()

    def select_button(self):
        new_menu = self.current_menu.selection()
        if new_menu is not None:
            self.current_menu = new_menu
        elif self.current_menu.parent:
            self.current_menu = self.current_menu.parent
        self._update_display()
        self.current_menu.select(0)

    def toggle_mute(self):
        if self.radio.muted:
            self.radio.unmute()
            self.display.set_muted(False)
        else:
            self.radio.mute()
            self.display.set_muted(True)

    #     # is wifi on? what's the strength?
    #     if self.wifi_manager.isWifiConnected():
    #         if self.wifi_manager.get_wifi_strength() >= -45: wifistatus =  ".  "
    #         elif self.wifi_manager.get_wifi_strength() >= -65: wifistatus = ".o "
    #         else: wifistatus = ".oO"
    #     else: wifistatus = " ? "

    def _update_display(self):
        self.display.update_menu_name(self.current_menu.title)
        self.display.update_menu_items(self.current_menu.items)
        self.display.finalize_body()

    def _schedule_ir_input(self, addr, data, _):
        """Defers handling of IR input outside of an IRQ"""
        micropython.schedule(self._ir_input, [addr, data])

    def register(self):
        """
        Register the badge with the MonkeyBadge server API
        """
        print("Doing checkin")
        baseurl = config.API_SERVER

        # get a handle from the server
        r = requests.get(baseurl + "/generate_handle")
        if r.status_code == 200:
            self.handle = r.text.strip("\"")
        else:
            self.handle = "unnamed_monkey"

        print("Running Badge Registration")
        print("UUID: %s, handle: %s" %(self.badge_uuid, self.handle))
        print("connecting to %s" % (baseurl + "/register"))
        print("Sending JSON Values: %s" %({"handle": self.handle,
                                   "key": self.registration_key,
                                   "myUUID": self.badge_uuid}))

        r = requests.post(baseurl + "/register",
                          json={"myUUID": self.badge_uuid,
                                "handle": self.handle,
                                "key": self.registration_key})
        json_data = json.loads(r.text)
        if 'UUID' in json_data and r.status_code == 200:
            print("badge registered")
            self.apitoken = json_data['token']
            self.db.set("token", self.apitoken)
        else:
            print("badge not registered.")

    def save_gamestate(self, state):
        """
        json_data is a json string from the server
        """
        new_state = json.loads(state) # convert from string to json

        try:
            current_state = json.loads(self.db.get("state"))
        except:
            print("No current state to load")
            current_state = ""
        #print(f"Current State {type(current_state)}: {current_state}")
        #print(f"New State {type(new_state)}: {new_state}")

        if current_state == new_state:
            print("gamestate unchanged")
        else:
            self.db.set("state", json.dumps(new_state))
            print("wrote gamestate to localdb")

    async def load_gamestate(self):
        if self.apitoken:
            while True:
                j = json.loads(self.db.get("state"))
                if j:
                    print("loaded gamestate from localdb")
                    #print(f"type: {type(j)} data: {j}")
                    self.handle = j['badgeHandle']
                    self.apitoken = j['token']
                    self.IR_ID = j['IR_ID']
                    self.current_challenge = j['current_challenge']
                    self.challenge1 = j['challenge1']
                    self.challenge2 = j['challenge2']
                    self.challenge3 = j['challenge3']
                    self.intro = j['intro']
                else:
                    print("No state to load")
                print(f"{self.intro}")
                if self.current_challenge == "intro" and self.intro['enabled'] == 1 and self.intro['complete'] == 0:
                    print("Konami code goes here")

                await asyncio.sleep(65)  # non-blocking wait for 1 minute


    async def checkin(self):
        """
        Checkin with the MonkeyBadge server API
        """
        if self.wifi_manager.isWifiConnected():

            while True:
                if not self.apitoken:
                    print("No API token, registering badge")
                    self.register()
                try:
                    print("Running check-in")
                    baseurl = config.API_SERVER

                    print("connecting to %s" % (baseurl + "/checkin"))

                    print("token: %s, uuid: %s" %(self.apitoken, self.badge_uuid))
                    r = requests.post(baseurl + "/checkin",
                                    headers={'X-API-Key': self.apitoken },
                                    json={"myUUID": self.badge_uuid})
                    #print(f"server response: {r.text}")
                    if r.status_code == 200:
                        self.save_gamestate(r.text)
                        print("badge checked in.")
                    else:
                        print("badge not registered.")
                except Exception as e:
                    print("Error making API call:", e)
                await asyncio.sleep(60)  # non-blocking wait for 1 minute
        else:
            print("Wifi is not connected, skipping checkin.")

    async def wifi_check(self):
        """
        Checkin with the MonkeyBadge server API
        """
        while True:
            if self.wifi_manager.isWifiConnected():
                print("Wifi is connected")
            else:
                print("Wifi is not connected, trying to connect.")
                await self.wifi_manager.connect()
            await asyncio.sleep(60)

    async def run(self):

        # Setup WiFi
        await self.wifi_manager.connect()

        print(f"Radio tuned to {self.radio.getFreq()}")

        # Setup button handler
        self.button_handler = ButtonHandler(config.BUTTON_PINS)
        self.button_handler.set_callback(self._button_callback)

        # Create tasks
        button_check_task = asyncio.create_task(self.button_handler.check_buttons())
        checkin_task = asyncio.create_task(self.checkin())
        state_task = asyncio.create_task(self.load_gamestate())
        network_check_task = asyncio.create_task(self.wifi_check())

        # always boot up to the main menu.
        self.current_menu = self.main_menu
        self._update_display()

        while True:
            await asyncio.gather(button_check_task, checkin_task, state_task, network_check_task)
