import time
import uasyncio as asyncio
from dimmer import Dimmer

'''
def demo():
    dim = Dimmer(2, 5000)
    dim.on()
    print(dim.sensor_values)
    print("on")
    time.sleep(1)
    dim.off()
    print(dim.sensor_values)
    print("off")
    time.sleep(1)
    print("blink")
    dim.blink(200, 2000, 0)
    #dim.blink1()
    time.sleep(5)
    dim.stop_blink()
    print("fading")
    dim.fading(10, 1000, 5)
    dim.off()
'''
def test_async():
    relay = Dimmer(2)
    asyncio.create_task(relay.async_blink())
    for i in range(0,10):
        print(i)
        if i == 4:
            relay.stop_async_blink()
        await asyncio.sleep(1)
    asyncio.create_task(relay.async_fading(10, 1000))
    for i in range(0,30):
        print(i)
        if i == 20:
            relay.stop_async_fading()
        await asyncio.sleep(1)

def demo_async():
    try:
        asyncio.run(test_async())
    finally:
        asyncio.new_event_loop()
if __name__ == "__main__":
    #demo()
    demo_async()
