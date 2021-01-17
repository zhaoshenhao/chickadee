import logging
from wifi import Wifi
import uasyncio as asyncio
import hw

async def demo_async():
    wifi = Wifi('ybb-home')
    print(wifi.check_wifi_config())
    print(await wifi.async_connect())
    await asyncio.sleep(1)
    print(wifi.get_info())
    asyncio.create_task(wifi.monitor())
    for i in range(0, 50):
        print(i)
        if i == 15:
            print("test disconnection")
            wifi.disconnect()
        await asyncio.sleep(1)

if __name__ == "__main__":
#    demo()
    try:
        logging._level = logging.DEBUG
        hw.WIFI_CHECK_INTVAL = 3
        asyncio.run(demo_async())
    finally:
        asyncio.new_event_loop()
