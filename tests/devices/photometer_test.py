# Light sensor
from photometer import Photometer

def demo():
    import time
    ds = Photometer(32)
    for _ in range(0, 5):
        print(ds.sensor_values)
        print(ds.get_light())
        time.sleep(1)

def demo_async():
    import uasyncio as asyncio
    ds = Photometer(32)
    for _ in range(0, 5):
        print(await ds.async_sensor_values())
        print(ds.get_light())
        await asyncio.sleep(1)

if __name__ == "__main__":
    demo()
    import uasyncio as asyncio
    asyncio.run(demo_async())
