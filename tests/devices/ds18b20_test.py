# Class for DS18B20 温度传感器
from ds18b20 import Ds18b20

def demo():
    import time
    ds = Ds18b20(4)
    for _ in range(0,2):
        print(ds.get_temperature())
        print(ds.sensor_values)
        time.sleep(1)

def demo_async():
    import uasyncio as asyncio
    ds = Ds18b20(4)
    for _ in range(0,2):
        print(ds.get_temperature())
        print(await ds.async_sensor_values())
        await asyncio.sleep(1)

if __name__ == "__main__":
    demo()
    import uasyncio as asyncio
    asyncio.run(demo_async())
