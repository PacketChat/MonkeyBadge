import uasyncio as asyncio
import urequests as requests
import ujson as json
import re 

import config  # Import the config file

from library import wifi
from library.menu import Menu, MenuItem
from library.menu import DisplayHandler
from library.button import ButtonHandler
from library import gameclient

display = DisplayHandler(config.OLED_WIDTH, config.OLED_HEIGHT, config.OLED_SDA_PIN, config.OLED_SCL_PIN)

# Button Callback
def button_callback(button_idx):
    global current_menu
    if button_idx == 0:  # 'up'
        current_menu.move_up()
    elif button_idx == 1:  # 'down'
        current_menu.move_down()
    elif button_idx == 2:  # 'select'
        selected_menu = current_menu.select()
        if selected_menu is not None:
            current_menu = selected_menu
            current_menu.update_display()

# Initialize DisplayHandler
display_handler = DisplayHandler(width=128, height=64, sda_pin=4, scl_pin=5)

# Example actions for menu items
def change_setting():
    # Implement setting change logic
    pass

def back_to_parent_menu(current_menu):
    return current_menu.parent

# Constructing Submenus
volume_menu = Menu([
    MenuItem("Increase", change_setting),
    MenuItem("Decrease", change_setting),
    MenuItem("Back", None, submenu=current_menu)
], display_handler)

settings_menu = Menu([
    MenuItem("Brightness", change_setting),
    MenuItem("Volume", None, submenu=volume_menu),
    MenuItem("Back", None, submenu=current_menu)
], display_handler)

# Main menu items
menu_items = [
    MenuItem("Status", change_setting),
    MenuItem("Settings", None, submenu=settings_menu),
    # Add more items
]

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

    # Initialize Main Menu
    main_menu = Menu(menu_items, display_handler)
    current_menu = main_menu
    current_menu.update_display()

    # Setup button handler
    button_handler = ButtonHandler(config.BUTTON_PINS)
    button_handler.set_callback(button_callback)
    print("button handler callback set")

    # Create tasks
    button_check_task = asyncio.create_task(button_handler.check_buttons())
    checkin_task = asyncio.create_task(badge.checkin())

    # Run tasks concurrently
    while True:
        await asyncio.gather(button_check_task, checkin_task)
    
# Run the main function
asyncio.run(main())
