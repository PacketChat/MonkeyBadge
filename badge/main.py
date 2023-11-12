import uasyncio as asyncio
import re 

import config  # Import the config file

from library import wifi
from library.menu import Menu, MenuItem
from library.display import DisplayHandler
from library.button import ButtonHandler
from library import gameclient
from library.leds import LEDHandler

# initialize the global display handler
display = DisplayHandler(config.OLED_WIDTH, config.OLED_HEIGHT, config.OLED_SDA_PIN, config.OLED_SCL_PIN)

# initialize the global led handler
leds = LEDHandler()

def init_menus(display_handler):
    """
    Initialize the menus before the callback buttons are set
      
    :param display_handler: DisplayHandler object
    
    :return: Main menu
    """
    # Placeholder actions
    def change_setting():
        pass  # Implement setting change logic

    main_menu = Menu([], display_handler, title="Main")
    radio_menu = Menu([], display_handler, title="Radio", parent=main_menu)
    settings_menu = Menu([], display_handler, title="Settings", parent=main_menu)
    lightshow_menu = Menu([], display_handler, title="LED Demos", parent=main_menu)
    ir_menu = Menu([], display_handler, title="Infrared", parent=main_menu)
    about_menu = Menu([], display_handler, title="About", parent=main_menu)

    main_menu.items.extend([
        MenuItem("Radio", submenu=radio_menu),
        MenuItem("Settings", submenu=settings_menu),
        MenuItem("Lightshow", submenu=lightshow_menu),
        MenuItem("IR", submenu=ir_menu),
        MenuItem("About", submenu=about_menu)
    ])
    about_menu.items.extend([
        MenuItem("Version", change_setting),
        MenuItem("Credits", change_setting),
        MenuItem("License", change_setting)
    ])
    ir_menu.items.extend([
        MenuItem("Send Message", change_setting),
        MenuItem("Receive Message", change_setting)
    ])  
    radio_menu.items.extend([
        MenuItem("Join Network", change_setting),
        MenuItem("Create Network", change_setting),
        MenuItem("Scan Networks", change_setting),
        MenuItem("Disconnect", change_setting)
    ])
    settings_menu.items.extend([
        MenuItem("OLED Brightness", change_setting),
        MenuItem("LED Brightness", change_setting),
        MenuItem("Volume", change_setting),
        MenuItem("Debounce", change_setting),
        MenuItem("OTA Update", change_setting),
        MenuItem("Reset Badge", change_setting)
    ])
    lightshow_menu.items.extend([
        MenuItem("popcorn", "leds.do_popcorn_effect()"),
        MenuItem("strobe", "leds.do_strobe()"),
        MenuItem("roll call", "leds.do_monkey_roll_call()")
    ])
    return main_menu

current_menu = None

def button_callback(button_idx):
    global current_menu
    if button_idx == 0:  # 'up'
        current_menu.move_up()
    elif button_idx == 1:  # 'down'
        current_menu.move_down()
    elif button_idx == 2:  # 'select'
        new_menu = current_menu.select()
        if new_menu is not None:
            current_menu = new_menu
        elif current_menu.parent:
            current_menu = current_menu.parent
        current_menu.update_display()
            
async def main():
    global current_menu  # Refer to the global current_menu

    display.clear()

    print("Badge Booting")
    display.print_logo()
    leds.do_rainbow_cycle(speed=1)

    # Setup WiFi
    wifi_manager = wifi.WiFiManager(config.WIFI_SSID, config.WIFI_PASSWORD)
    await wifi_manager.connect()
    print(f"wifi connected: \n {wifi_manager.get_status()}")

    # startup the badge, use the mac as the UUID
    mymac = re.sub(':', '-', str(wifi_manager.get_mac()))
    badge = gameclient.MonkeyBadge(mymac)

    main_menu = init_menus(display)
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
