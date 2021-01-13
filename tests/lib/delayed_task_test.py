import uasyncio
from utils import delayed_task

def t1(b1=True, b2=True):
    print(b1)
    print(b2)

async def test():
    delayed_task(5000, t1, (True, True))
    await uasyncio.sleep(10)

uasyncio.run(test())
