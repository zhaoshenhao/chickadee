import uasyncio as asyncio

def f(p1):
    print("Hi f: ", p1)

async def af(p):
    print("Hi af", p)

async def aaf(p):
    print("Hi aaf", p)
    await asyncio.sleep(0)

async def test():
    f(1)
    f(2)
    await af(1)
    await aaf(1)
    await asyncio.sleep(5)

asyncio.run(test())