import asyncio
import config
import network
from library.display import DisplayHandler
from library.ota.update import OTA


async def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(ssid, password)

        # Wait for the connection to be established, timeout after 30 seconds
        for _ in range(30):
            await asyncio.sleep(1)
            if wlan.isconnected():
                print("Wi-Fi connected!")
                await check_ota()
                break
        else:
            print("Wi-Fi connection timeout.")


async def check_ota():
    # TODO: Set this to false before shipping
    try:
        with OTA(reboot=True, verbose=False) as ota:
            ota.from_json(config.UPDATE_URL)
    except Exception:
        pass


display = DisplayHandler(
    config.OLED_WIDTH,
    config.OLED_HEIGHT,
    config.OLED_SDA_PIN,
    config.OLED_SCL_PIN,
)

print("Performing power on OTA check")
display.display.fill(0)
display.display.text("   Performing", 0, 12)
display.display.text("   OTA Update", 0, 20)
display.display.show()
asyncio.run(connect_to_wifi(config.WIFI_SSID, config.WIFI_PASSWORD))
del display
