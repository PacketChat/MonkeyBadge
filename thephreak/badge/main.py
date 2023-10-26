import uasyncio as asyncio
import urequests as requests
import ujson as json
import re 

import config  # Import the config file

from library import wifi
from library.menu import Menu
from library.menu import DisplayHandler
from library.button import ButtonHandler
from library import gameclient


display = DisplayHandler(config.OLED_WIDTH, config.OLED_HEIGHT, config.OLED_SDA_PIN, config.OLED_SCL_PIN)

# Menu Hierarchy
about_menu = Menu("About", [Menu("Test LEDs", [])])
settings_menu = Menu("Settings", [Menu("Volume", []), Menu("Brightness", [])])
main_menu = Menu("Main", [Menu("Status", []), Menu("Radio", []), Menu("MatchMode", []), settings_menu, about_menu])

current_menu = main_menu

def button_callback(index):
    global current_menu

    if index == 0: # UP
        current_menu.prev_item()
    elif index == 1: # DOWN
        current_menu.next_item()
    elif index == 2: # SELECT
        current_menu = current_menu.select()
    elif index == 3: # BACK
        current_menu = current_menu.back()
    
    current_menu.display(display)

async def main():
    display.clear()
    display.print_text(["Badge Booting", "Please Wait..."])

    # Setup WiFi
    wifi_manager = wifi.WiFiManager(config.WIFI_SSID, config.WIFI_PASSWORD)
    await wifi_manager.connect()
    print("wifi connected")
    # startup the badge, use the mac as the UUID
    mymac = re.sub(':', '-', str(wifi_manager.get_mac()))
    badge = gameclient.MonkeyBadge(mymac)
    # Setup button handler
    button_handler = ButtonHandler(config.BUTTON_PINS)
    button_handler.set_callback(button_callback)
    print("button handler callback set")
    # Display the initial menu
    current_menu.display(display)
    print("got here")
    
    # Create tasks
    button_check_task = asyncio.create_task(button_handler.check_buttons())
    checkin_task = asyncio.create_task(badge.checkin())

    # Run tasks concurrently
    while True:
        await asyncio.gather(button_check_task, checkin_task)
    
# Run the main function
asyncio.run(main())
