# DHT11 温度、湿度传感器
from hcsr04 import HCSR04
import uasyncio as asyncio
import time

async def demo_async():
    ds = HCSR04()
    for _ in range(0,2):
        print(await ds.async_sensor_values())
        print(ds.get_distance())
        await asyncio.sleep(1)

def demo():
    ds = HCSR04()
    for _ in range(0,2):
        print(ds.sensor_values)
        print(ds.get_distance())
        time.sleep(1)

if __name__ == "__main__":
    demo()
    import uasyncio as asyncio
    asyncio.run(demo_async())
