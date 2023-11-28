from machine import Pin
import micropython
import network
import time

import ujson as json

from library.ir import IR
from library import konami
from library.button import ButtonHandler
from library.db import dbtree
from library.display import DisplayHandler
from library.gameclient import GameClient
from library.leds import LEDHandler
from library.menu import Menu, MenuItem
from library.radio import SI470X
import library.wifi as wifi

#from library.ir_rx.nec import NEC_16 as NECRx
import config  # Import the config file
import re

__version__ = '0.2.0'

class MonkeyBadge:
    def __init__(self):
        """
        Initalize the MonkeyBadge class - this class is used to interact with the MonkeyBadge server API
        :param uuid: The UUID of the badge
        """
        # anything in the calls queue should return true on success and false
        # on failure
        self._calls_queue = list()
        # radio init
        self.radio = SI470X()
        self.radio.setVolume(1)

        self.db = dbtree()

        self.gameclient = GameClient()
        self.last_checkin = -60000

        # Wifi Init
        self.wlan = network.WLAN(network.STA_IF)

        # Display Init
        self.display = DisplayHandler(config.OLED_WIDTH,
                                      config.OLED_HEIGHT,
                                      config.OLED_SDA_PIN,
                                      config.OLED_SCL_PIN)
        self._log = []

        # Led init
        self.leds = LEDHandler()

        # IR
        self.infrared = IR()
        self.seen_badges = dict()

        # boot
        print("Badge Booting")
        self.display.print_logo()


        # TODO possibly set this as a property of the game client
        self.registration_key = config.REG_KEY
        self.current_menu = None

        # Need to pull these from the db store.
        try:
            self.apitoken = self.db.get("token")
        except:
            print("Unable to load token: badge not registered.")
            self.apitoken = None

        self.lock_radio_station = False
        self.handle = None
        self.current_challenge = None
        self.challenge1 = {}
        self.challenge2 = {}
        self.challenge3 = {}
        self.intro = {"complete": False, "enabled": False}

        # use the mac as the UUID
        self.badge_uuid = re.sub(':', '-', str(wifi.get_mac(self.wlan)))
        print("Badge UUID: %s" % (self.badge_uuid))

        # Menu Definitions
        self.main_menu = Menu([], title="Main")
        self.radio_menu = Menu([], title="Radio", parent=self.main_menu)
        self.settings_menu = Menu([], title="Settings", parent=self.main_menu)
        self.lightshow_menu = Menu([], title="LED Demos", parent=self.main_menu)
        self.ir_menu = Menu([], title="Infrared", parent=self.main_menu)
        self.social_menu = Menu([], title="Social", parent=self.main_menu)
        self.about_menu = Menu([], title="About", parent=self.main_menu)

        self.volume_menu = Menu([], title="Volume", parent=self.radio_menu)
        self.volume_menu.items.extend([
            MenuItem("Volume", self.donothing, dynamic_text=self.display_vol),
            MenuItem("Volume Up", self.menu_volume_up),
            MenuItem("Volume Down", self.menu_volume_down)
        ])
        self.challenge_menu = Menu([],
                                     title='Chlng Status',
                                     parent=self.about_menu)
        self.main_menu.items.extend([
            MenuItem("Radio", submenu=self.radio_menu),
            MenuItem("Settings", submenu=self.settings_menu),
            MenuItem("Lightshow", submenu=self.lightshow_menu),
            MenuItem("IR", submenu=self.ir_menu),
            MenuItem("Social", submenu=self.social_menu),
            MenuItem("About", submenu=self.about_menu),
        ])
        self.about_menu.items.extend([
            MenuItem("Version", self.display_menu('Version', __version__)),
            MenuItem("Chllnge Status", submenu=self.challenge_menu),
            MenuItem("Credits", self.display_menu('Credits',
                                                  'temtel',
                                                  'crackerjack',
                                                  'thephreak',
                                                  'faxanadu',
                                                  'redbeard',
                                                  'numeral')),
            MenuItem("License", self.display_menu('License',
                                                  "The Don't",
                                                  'Ask Me',
                                                  'About It',
                                                  'License',
                                                  '',
                                                  'Copying and',
                                                  'distribution',
                                                  'of this code,',
                                                  'with or',
                                                  'without',
                                                  'modification,',
                                                  'are permitted',
                                                  'in any medium',
                                                  'provided you',
                                                  'do not',
                                                  'contact the',
                                                  'author about',
                                                  'the code or',
                                                  'any problems',
                                                  'you are',
                                                  'having with',
                                                  'the code',
                                                  )),
            MenuItem("Log", self.select_log),
        ])
        self.ir_menu.items.extend([
            MenuItem("Send Message", "pass"),
            MenuItem("Receive Message", "pass")
        ])
        self.social_menu.items.extend([
            MenuItem("Find Badges", self.find_badges),
            MenuItem("Seen Badges", self.seen_badges_action),
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

    @property
    def infrared_id(self):
        return self.infrared.self_addr

    @infrared_id.setter
    def infrared_id(self, addr):
        self.infrared.set_my_address(addr)

    @property
    def log(self):
        """Returns badge log"""
        return self._log

    @log.setter
    def log(self, msg):
        self._log.append(msg)
        self._log = self._log[-8:]

    def if_wifi(func):
        """Decorator to only run if wifi is enabled"""
        def _f(self, *args, **kwargs):
            if self.wlan.isconnected():
                return func(self, *args, **kwargs)
        return _f

    def if_ir(func):
        """Decorator to only run if IR is enabled"""
        def _f(self, *args, **kwargs):
            if self.infrared.enabled:
                return func(self, *args, **kwargs)
        return _f

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

    # social wrappers
    def find_badges(self):
        n = self.infrared.send_discover()
        if n == 0:
            self.log = 'findbadge fail'

    def seen_badges_action(self):
        now = time.ticks_ms()
        sbmenu = Menu([], 'Seen Badges', parent=self.current_menu)
        sbmenu.items.extend([
            MenuItem(f'{badge}: {time.ticks_diff(now, last_seen)//1000}s ago')
            for badge, last_seen in self.seen_badges.items()
        ])
        return sbmenu

    def select_log(self):
        lmenu = Menu([], 'Log', parent=self.current_menu)
        lmenu.items.extend([
            MenuItem(f'{log}') for log in self.log
        ])
        return lmenu

    def display_menu(self, name, *args):
        def _f():
            print(name, args)
            dmenu = Menu([], name, parent=self.current_menu)
            dmenu.items.extend([
                MenuItem(arg) for arg in args
            ])
            return dmenu
        return _f

    # noop
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
            print("Unable to load saved state: not found.")
            current_state = ""
        # print(f"Current State {type(current_state)}: {current_state}")
        # print(f"New State {type(state)}: {state}")

        if current_state == state:
            print("gamestate unchanged")
        else:
            self.db.set("state", json.dumps(state))
            print("Saved gamestate to localdb")

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
            print("loaded gamestate {}".format(self.infrared_id))
            self.handle = j['badgeHandle']
            self.apitoken = j['token']
            self.infrared_id = j['IR_ID']
            if self.intro['complete'] != j['intro']['complete'] and \
                    j['intro']['complete']:
                self.challenge_menu.items.append(MenuItem('Intro Complete',
                                                          self.donothing))
            self.intro = j['intro']
            if not self.infrared.pairing and self.intro['complete']:
                self.infrared.enable_pairing()
            self.challenge1 = j['challenge1']
            self.challenge2 = j['challenge2']
            self.challenge3 = j['challenge3']
            self.current_challenge = j['current_challenge']
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
            print("registration successful")
            self.apitoken = r['token']
            self.db.set("token", self.apitoken)
        else:
            print("registration failed")

    def clean_seen_badges(self, now):
        """Cleans badges we haven't seen in a while"""
        for badge, last_seen in self.seen_badges.items():
            if time.ticks_diff(now, last_seen) > config.CLEAN_BADGE_AFTER:
                del self.seen_badges[badge]

    @if_wifi
    def config_konami_win(self):
        """We've completed the intro challenge"""
        j = self.gameclient.konami_complete(self.apitoken, self.badge_uuid)
        if j is None:
            return False
        self.load_gamestate(j)
        return True

    @if_wifi
    def checkin(self):
        """
        Checkin with the MonkeyBadge server API
        """
        if not self.apitoken:
            print("No API token, registering badge")
            self.register()
        else:
            print("checking in badge")
            r = self.gameclient.checkin(self.apitoken, self.badge_uuid)
            if r:
                self.save_gamestate(r)
                self.load_gamestate(r)
                print("Badge successfully checked in")
            else:
                print("Badge checkin failed")
        # time.sleep_ms(config.CHECKIN_PERIOD * 1000)


    @if_ir
    def infrared_check(self):
        if self.infrared.msgs:
            print('infrared check')
            while self.infrared.msgs:
                opcode, sender, extra = self.infrared.msgs.pop()
                if opcode == 'DISCOVER':
                    self.log = f'DISC: {sender}'
                    self.infrared.send_here()
                elif opcode == 'HERE':
                    self.log = f'HERE: {sender}'
                    self.seen_badges[sender] = time.ticks_ms()
                elif opcode == 'INIT_PAIR':
                    self.log = f'PAIR: {sender}'
                    self.infrared.send_resp_pair(sender)

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
        # checkin_task = asyncio.create_task(self.checkin())
        # network_check_task = asyncio.create_task(self.wifi_check())
        # infrared_task = asyncio.create_task(self.infrared_check())
        # ir_recv_task = asyncio.create_task(self.infrared.recv())
        # tasks = {
        #         'checkin_task': checkin_task,
        #         'network_check_task': network_check_task,
        #         'infrared_check_task': infrared_task,
        #         'ir_recv_task': ir_recv_task,
        # }

        # always boot up to the main menu.
        self.current_menu = self.main_menu
        self._update_display()

        # turn on IR Recv
        self.infrared.enable_sync()
        self.display.set_ir_status(True)

        # return tasks

    def deinitialize(self):
        self.infrared.disable()

    def run(self):
        # self.leds.set_led_lights('do_boot_sequence')
        self.initialize_badge()
        # main controller
        while True:
            now = time.ticks_ms()

            current_calls = self._calls_queue[:]
            self._calls_queue = list()
            for call in current_calls:
                success = call()
                if not success:
                    self._calls_queue.append(call)

            # wlan, no blocking
            print(self.wlan.ifconfig()[0], self.last_checkin, now)
            if not self.wlan.isconnected():
                self.display.set_wifi_status(None)
                self.wlan.active(True)
                self.wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
            else:
                self.display.set_wifi_status(int(self.wlan.status('rssi')))

            # checkin, blocking
            if time.ticks_diff(now,
                               self.last_checkin) >= config.CHECKIN_PERIOD:
                self.checkin()
                self.last_checkin = now

            # update ir status
            self.display.set_ir_status(self.infrared.enabled)
            # handle ir msgs
            self.infrared_check()
            # clean seen badges
            self.clean_seen_badges(now)

            # check whether we should move to intro mode
            if self.intro['complete'] == 0 and \
                    self.config_konami_win not in self._calls_queue and \
                    self.intro['enabled'] == 1 and \
                    self.current_challenge == "intro":
                self.deinitialize()
                # konami.main()
                self.initialize_badge()
                self._calls_queue.append(self.config_konami_win)
            self.display.refresh()
            time.sleep(5)