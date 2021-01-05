# BMP280 气压，温度，海拔（误差较大）
from bmp280 import Bmp280
import uasyncio as asyncio
import time

async def demo_async():
    ds = Bmp280(16, 17)
    for _ in range(0,2):
        print(await ds.async_sensor_values())
        print(ds.get_temperature())
        print(ds.get_pressure())
        print(ds.get_altitude())
        await asyncio.sleep(1)

def demo():
    ds = Bmp280(16, 17)
    for _ in range(0,2):
        print(ds.sensor_values)
        print(ds.get_temperature())
        print(ds.get_pressure())
        print(ds.get_altitude())
        time.sleep(1)

if __name__ == "__main__":
    demo()
    import uasyncio as asyncio
    asyncio.run(demo_async())

