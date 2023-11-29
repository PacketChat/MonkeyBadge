import asyncio
import config
import network
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

    with OTA(verbose=True) as ota:
        ota.from_json(config.UPDATE_URL)

print("Performing POST")
print("Preforming power on OTA check")
asyncio.run(connect_to_wifi(config.WIFI_SSID, config.WIFI_PASSWORD))

