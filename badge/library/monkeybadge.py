from machine import Pin
import micropython

import ujson as json
import uasyncio as asyncio

#from library import konami
from library.button import ButtonHandler
from library.db import dbtree
from library.display import DisplayHandler
from library.leds import LEDHandler
from library.menu import Menu, MenuItem
from library.radio import SI470X
from library.wifi import WiFiManager
from library.gameclient import GameClient

#from library.ir_rx.nec import NEC_16 as NECRx
import config  # Import the config file
import re

class MonkeyBadge:
    def __init__(self):
        """
        Initalize the MonkeyBadge class - this class is used to interact with the MonkeyBadge server API
        :param uuid: The UUID of the badge
        """
        # radio init
        self.radio = SI470X()
        self.radio.setVolume(1)
        self.db = dbtree()
        self.gameclient = GameClient()

        # Wifi Init
        self.wifi_manager = WiFiManager(config.WIFI_SSID, config.WIFI_PASSWORD)

        # Display Init
        self.display = DisplayHandler(config.OLED_WIDTH, config.OLED_HEIGHT, config.OLED_SDA_PIN, config.OLED_SCL_PIN)

        # Led init
        self.leds = LEDHandler()

        # boot
        print("Badge Booting")
        self.display.print_logo()

        # self.leds.set_led_lights('do_boot_sequence')

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
        self.intro = {"complete": False, "enabled": False}

        # use the mac as the UUID
        self.macid = re.sub(':', '-', str(self.wifi_manager.get_mac()))
        self.badge_uuid = self.macid
        print("Badge UUID: %s" % (self.badge_uuid))

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
            MenuItem("OTA Update", "pass"),
            MenuItem("Reset Badge", "pass")
        ])

        def _lightshow(name, *args, **kwargs):
            def _f():
                self.leds.set_led_lights(name, *args, **kwargs)
                return self.current_menu
            return _f

        self.lightshow_menu.items.extend([
            MenuItem("popcorn", _lightshow('do_popcorn_effect')),
            MenuItem("roll call", _lightshow('do_monkey_roll_call')),
            MenuItem("heartbeat", _lightshow('do_heartbeat')),
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

    def display_freq(self):
        return f"FM: {self.radio.getFreq()}"

    def display_vol(self):
        return f"Volume: {self.radio.volume}"

    def donothing(self):
        return self.current_menu

    def _left_up_butback(self):
        index = self.display.menu_up()
        self.current_menu.select(index)

    def _left_down_butback(self):
        index = self.display.menu_down()
        self.current_menu.select(index)

    def _center_butback(self):
        self.select_button()

    def _right_butback(self):
        self.toggle_mute()

    def select_button(self):
        new_menu = self.current_menu.selection()
        if new_menu is not None:
            self.current_menu = new_menu
        self._update_display(menu_index=self.current_menu.selected)

    def toggle_mute(self):
        if self.radio.muted:
            self.radio.unmute()
            self.display.set_muted(False)
        else:
            self.radio.mute()
            self.display.set_muted(True)

    def _update_display(self, menu_index=0):
        self.display.update_menu_name(self.current_menu.title)
        self.display.update_menu_items(self.current_menu.items, menu_index)
        self.display.finalize_body()  # write

    def _schedule_ir_input(self, addr, data, _):
        """Defers handling of IR input outside of an IRQ"""
        micropython.schedule(self._ir_input, [addr, data])

    def save_gamestate(self, state):
        """
        json_data is a json string from the server
        """
        try:
            current_state = json.loads(self.db.get("state"))
        except:
            print("No current state to load")
            current_state = ""
        #print(f"Current State {type(current_state)}: {current_state}")
        #print(f"New State {type(new_state)}: {new_state}")

        if current_state == state:
            print("gamestate unchanged")
        else:
            self.db.set("state", json.dumps(state))
            print("wrote gamestate to localdb")

    def load_gamestate(self, payload=None):
        if payload:
            print('loading from argument')
            j = payload
        else:
            state = self.db.get('state')
            if not state:
                return
            j = json.loads(state)

        if j:
            print("loaded gamestate from localdb")
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

    def register(self):
        request_body = {
            "handle": self.handle,
            "key": self.registration_key,
            "myUUID": self.badge_uuid
            }

        r = self.gameclient.reg_request(request_body)

        if r:
            print("registeration successful")
            self.apitoken = r['token']
            self.db.set("token", self.apitoken)
        else:
            print("registration failed")

    async def checkin(self):
        """
        Checkin with the MonkeyBadge server API
        """
        while True:
            print('Badge checkin loop')
            if self.wifi_manager.isWifiConnected():
                if not self.apitoken:
                    print("No API token, registering badge")
                    self.register()
                else:
                    print("checking in badge")
                    r = self.gameclient.checkin(self.apitoken, self.badge_uuid)
                    if r:
                        self.save_gamestate(r.json())
                        self.load_gamestate(r.json())
                        print("Badge successfully checked in")
                    else:
                        print("Badge checkin failed")
            else:
                print("Wifi is not connected, skipping checkin.")
            await asyncio.sleep(config.CHECKIN_PERIOD)

    async def wifi_check(self):
        """
        Checkin with the MonkeyBadge server API
        """
        while True:
            print('wifi check loop')
            if self.wifi_manager.isWifiConnected():
                self.display.set_wifi_status(
                        self.wifi_manager.get_wifi_strength())
            else:
                if await self.wifi_manager.connect():
                    self.display.set_wifi_status(
                            self.wifi_manager.get_wifi_strength())
                else:
                    self.display.set_wifi_status(None)
            await asyncio.sleep(60)

    def initialize_badge(self):
        """Do the whole setup thing dawg"""
        self.load_gamestate()

        # Setup button handler
        self.button_handler = ButtonHandler(
                self._left_up_butback,
                self._left_down_butback,
                self._center_butback,
                self._right_butback
        )

        # Create tasks
        checkin_task = asyncio.create_task(self.checkin())
        network_check_task = asyncio.create_task(self.wifi_check())
        tasks = {
                'checkin_task': checkin_task,
                'network_check_task': network_check_task
        }

        # always boot up to the main menu.
        self.current_menu = self.main_menu
        self._update_display()

        return tasks

    def deinitialize(self, tasks):
        for task in tasks.values():
            task.cancel()

    async def run(self):
        tasks = self.initialize_badge()
        # main controller
        while True:
            for task in tasks:
                if tasks[task].done():
                    print(f'error: {task}')
            print('game loop')
            self.display.ticker.queue('konami code does not go here')
            print(self.intro)
            if self.current_challenge == "intro" and \
                    self.intro['enabled'] == 1 and \
                    self.intro['complete'] == 0:
                pass
                # self.display.ticker.queue('konami code goes here')
                # self.deinitialize(tasks)
                # konami.main()
                # self.intro['complete'] == 1
                # tasks = self.initialize_badge()
            await asyncio.sleep(5)
