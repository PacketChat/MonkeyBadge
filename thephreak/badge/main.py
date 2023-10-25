import uasyncio as asyncio
import urequests as requests
import ujson as json
import re 

import config  # Import the config file

from lib import wifi
from lib import menu
from lib.button import ButtonHandler
from lib import gameclient

def display_mainmenu(display):
    display.clear()
    display.show_text("Main Menu","> Status", "> Radio", "> MatchMode", "> About")

async def main():
    display = menu.DisplayHandler(config.OLED_WIDTH, config.OLED_HEIGHT, config.OLED_SDA_PIN, config.OLED_SCL_PIN)
    display.clear()
    display.show_text("Badge Booting", "Please Wait...")

    # Setup WiFi
    wifi_manager = wifi.WiFiManager(config.WIFI_SSID, config.WIFI_PASSWORD)
    await wifi_manager.connect()

    # startup the badge, use the mac as the UUID
    mymac = re.sub(':', '-', str(wifi_manager.get_mac()))
    badge = gameclient.MonkeyBadge(mymac)

    display_mainmenu(display)

    # Initialize the button handler with the pins from the config file
    button_handler = ButtonHandler(config.BUTTON_PINS)

    # Create tasks
    button_check_task = asyncio.create_task(button_handler.check_buttons())
    checkin_task = asyncio.create_task(badge.checkin())

    # Run tasks concurrently
    while True:
        await asyncio.gather(button_check_task, checkin_task)
    
# Run the main function
asyncio.run(main())
