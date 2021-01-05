# For any relay/switch
from relay import Relay
import uasyncio as asyncio

async def test_async():
    relay = Relay(2)
    relay.on()
    print("on")
    asyncio.sleep(1)
    relay.off()
    print("off")
    asyncio.sleep(1)
    asyncio.create_task(relay.async_blink())
    for i in range(0,10):
        print(i)
        if i == 5:
            relay.stop_async_blink()
        await asyncio.sleep(1)

def demo_async():
    asyncio.run(test_async())

if __name__ == "__main__":
    #demo()
    demo_async()
