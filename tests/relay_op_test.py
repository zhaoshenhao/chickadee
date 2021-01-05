from op import Controller
import uasyncio as asyncio
import logging
from relay import Relay
from sys_op import SysOp
from consumer import DefaultConsumer

OP = 'op'

async def test(opc):
    param = {'op': 'on', 'on-ms': 100, 'off-ms': 500}
    print("Get state")
    x = await opc.op('relay', 'get', None)
    print(x)
    await asyncio.sleep(1)

    print("Set on")
    x = await opc.op('relay', 'set', param)
    print(x)
    await asyncio.sleep(2)

    print("Get state")
    x = await opc.op('relay', 'get', None)
    print(x)
    
    print("Set off")
    param[OP] = 'off'
    x = await opc.op('relay', 'set', param)
    print(x)
    await asyncio.sleep(2)

    print("Geet state")
    x = await opc.op('relay', 'get', None)
    print(x)

    print("Flip")
    param[OP] = 'flip'
    x = await opc.op('relay', 'set', param)
    print(x)
    await asyncio.sleep(2)

    print("Geet state")
    x = await opc.op('relay', 'get', None)
    print(x)
    await asyncio.sleep(2)

    print("blink")
    param[OP] = 'blink'
    x = await opc.op('relay', 'set', param)
    print(x)
    await asyncio.sleep(10)

    print('stop blink')
    param[OP] = 'stop-blink'
    x = await opc.op('relay', 'set', param)
    print(x)
    await asyncio.sleep(1)

    print('Get state')
    x = await opc.op('relay', 'get', None)
    print(x)

relay = Relay(2)
opc = Controller()
ops = []
ops.append(relay)
ops.append(DefaultConsumer())
opc.setup(ops)
print(opc.commands.keys())
try:
    asyncio.run(test(opc))
finally:
    asyncio.new_event_loop()


